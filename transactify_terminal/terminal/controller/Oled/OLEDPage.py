from django.dispatch import Signal

from PIL import Image, ImageDraw, ImageFont, ImageOps
import PIL.Image
import time
import base64
from io import BytesIO
from PIL import Image
import requests

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from OLEDViewController import OLEDViewController # to avoid circular import, only for type hinting

from ..ConfParser import Store
from ...api_endpoints.StoreProduct import StoreProduct
from ...api_endpoints.Customer import Customer

from random import randint
from luma.core.render import canvas

from terminal.controller.LEDStripController import LEDStripController
from terminal.webmodels.Store import Store

class OLEDPage():
    name: str = "OLEDPage"

    BTN_OKAY = "F"
    BTN_BACK = "E"
    
    def __init__(self, oled, 
                 sig_abort_view: Signal, sig_request_view: Signal,
                 sig_on_barcode_read: Signal, sig_on_nfc_read: Signal, sig_on_btn_pressed: Signal,
                 #
                 sign_on_websocket_connect: Signal, sign_on_websocket_disconnect: Signal,
                 #
                 view_controller,
                 ledstrip: LEDStripController,
                 locked = False, overwritable = True):
        
        self._signal_abort_view = sig_abort_view
        self._signal_request_view = sig_request_view

        self._signal_on_barcode_read = sig_on_barcode_read
        self._signal_on_nfc_read = sig_on_nfc_read
        self._signal_on_btn_pressed = sig_on_btn_pressed

        self._signal_on_websocket_connect = sign_on_websocket_connect
        self._signal_on_websocket_disconnect = sign_on_websocket_disconnect

        

        self.stores: list[Store] = list(Store.objects.filter(is_connected=True).order_by('terminal_button'))
        
        self.view_controller: OLEDViewController = view_controller

        self.ledstrip = ledstrip
        self.oled = oled

        OLEDPage.name: str = str(self.__class__.__name__)

        # Stores if the view has been locked. if locked, no interaction with the terminal is allowed. 
        # The view can be released by pressing button A.
        self.locked: bool = locked     

        # If the view sets the flag to Ture, it allows the Controller to  overwrite the view by another view.
        # Some views can be overwritten, some not.
        self.overwritable: bool = overwritable          
           
        self.image = None
        self.draw = None

        self.width = self.oled.width
        self.height = self.oled.height

        self.font_large = ImageFont.load_default(size=16)
        self.font_regular = ImageFont.load_default(size=12)
        self.font_small = ImageFont.load_default(size=10)
        self.font_tiny = ImageFont.load_default(size=8)

        # asyncronous event handling
        self._signal_abort_view.connect(self._abort_view)

        self._signal_on_barcode_read.connect(self._sig_on_barcode_read)
        self._signal_on_nfc_read.connect(self._sig_on_nfc_read)
        self._signal_on_btn_pressed.connect(self._sig_on_btn_pressed)

        self._signal_on_websocket_connect.connect(self._sig_on_websocket_connect)
        self._signal_on_websocket_disconnect.connect(self._sig_on_websocket_disconnect)
        
        self.break_loop = False
        self.is_active = False

        self.oled_image = None
        self.oled_image_base64 = None

    def _abort_view(self, sender, **kwargs):
        print(f"Aborting view {self.name}")
        self.break_loop = True

    def _post_init(self):
        self.image = Image.new(self.oled.mode, (self.width, self.height))  # Use oled.mode for compatibility
        self.draw = ImageDraw.Draw(self.image) 
        return self.image, self.draw

    @classmethod
    def class_name(cls):
        return cls.__name__
    
    def view(self,  kill_flag=False, *args, **kwargs,):
        raise NotImplementedError("View not implemented")
    
    def convert_image_to_base64(self, image):
        """
        Convert a PIL Image to Base64.
        """
        try:
            buffer = BytesIO()
            image.save(buffer, format="PNG")  # Save the image to a buffer
            buffer.seek(0)
            base64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")  # Encode and decode to a string
            return base64_data
        except Exception as e:
            print(f"Error converting image to Base64: {e}")
            return None
    
    def send_to_display(self, image):
        self.oled_image = image
        self.oled_image_base64 = self.convert_image_to_base64(image)
        # Broadcast the image to WebSocket clients
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "oled_display",  # Group name
            {
                "type": "display_image",
                "image_data": self.oled_image_base64,  # Convert image to bytes
            },
        )
        self.oled.display(self.oled_image)
    # =================================================================================================================
    # Display Helper functions
    # =================================================================================================================
    def paste_image(self, image, path, pos):
        try:
            symb = PIL.Image.open(path)
            symb = symb.convert('RGB')
            symb = ImageOps.invert(symb)
            image.paste(symb, pos)  # Paste at (2, 2) in the top-left corner
        except Exception as e:
            print(f"Error loading symbol: {e}")
            #symb = PIL.Image.open('/app/static/icons/png_16/coin.png')
            #symb = symb.convert('RGB')
            #symb = ImageOps.invert(symb)
            #image.paste(symb, pos)  # Paste at (2, 2) in the top-left corner

    def align_right(self, draw, text, pos_y, font):
        (w, h), (offset_x, offset_y) = font.font.getsize(text)
        pos_x = self.width - w
        pos_y = pos_y - h
        draw.text((pos_x, pos_y), text, font=font, fill=(255,255,255))    
        return w, h, pos_x, pos_y
    
    def align_center(self, draw, text, pos_y, font):
        (w, h), (offset_x, offset_y) = font.font.getsize(text)
        pos_x = (self.width - w) // 2
        pos_y = pos_y - h
        draw.text((pos_x, pos_y), text, font=font, fill=(255,255,255))    
        return w, h, pos_x, pos_y

    def display_next(self, image, draw, next_view, wait_time=20, *args, **kwargs):
            print(f"* Refreshing after {wait_time} seconds.")
            # use asyncio sleep
            for wt in range(wait_time, -1, -1):
                #print(f"Break loop? {self.break_loop}")
                if self.break_loop:
                    print("Loop breaked.")
                    self.break_loop = False
                    return
                #await asyncio.sleep(1)
                time.sleep(1)
                segment = int((self.width / wait_time) * wt)
                draw.line([(0, 20), (segment, 20)], fill=(255, 255, 255), width=1)
                draw.line([(segment, 20), (self.width, 20)], fill=(0,0,0), width=1)
                #draw.rectangle((pos_x-w, pos_y-y, pos_x + w, pos_y + h), fill="black")
                #w, h, pos_x, pos_y = self.align_right(draw, str(wt), 10, self.font_small)
                # clear the display w, h, pos_x, pos_y 
                print(f"> Displaying next view in {wt} seconds.")
                # print inline the countdown, no new line
                self.oled.display(image)
            if isinstance(next_view, OLEDPage):
                next_view = next_view.name
            self._signal_request_view.send(sender=self.name, view=next_view, *args, **kwargs)

    # =================================================================================================================
    # Display Overlays
    # =================================================================================================================
    def display_lock_overlay(self):
        print(f"Displaying lock overlay.")
        # Use the currecnt image and make a copy
        copy_image_content = self.image.copy()
        copy_draw_content = ImageDraw.Draw(copy_image_content)
        # overlay a rechatngel with a lock symbol
        img = r"/app/static/icons/png_32/lock.png"
        img_width,  img_heiht = PIL.Image.open(img).size
        center_x = self.width // 2
        center_y = self.height // 2
        img_pos_x = int(center_x - img_width  // 2)  # Size of image is 64x64
        img_pos_y = int(center_y - img_heiht // 2)  # Size of image is 64x64
        rect_x1 = int(img_pos_x - 10)
        rect_y1 = int(img_pos_y - 5)
        rect_x2 = int(img_pos_x + img_width + 10)
        rect_y2 = int(img_pos_y + img_heiht + 5)

        # create a black rectangle with white border
        copy_draw_content.rectangle((rect_x1, rect_y1, rect_x2, rect_y2), fill=(0,0,0), outline=(255,255,255), width=1)
        self.paste_image(copy_image_content ,img, (img_pos_x, img_pos_y))

        copy_draw_content.rectangle((0, rect_y2+1, self.width, self.height), fill=(0,0,0))
        self.align_center(copy_draw_content, "Terminal is locked. Press A to release", rect_y2 + 7, self.font_small)
       # self.align_center(copy_draw_content, "Press A to release", rect_y2 + 22, self.font_small)
        self.oled.display(copy_image_content)
        time.sleep(5)
        self.oled.display(self.image)

    def display_nfc_overlay(self, stage, display_check=False):
        print(f"Displaying lock overlay.")
        # Use the currecnt image and make a copy
        copy_image_content = self.image.copy()
        copy_draw_content = ImageDraw.Draw(copy_image_content)
        # overlay a rechatngel with a lock symbol
        img = r"/app/static/icons/png_24/NFC_logo.png"
        img_width,  img_heiht = PIL.Image.open(img).size
        center_x = self.width // 2
        center_y = self.height // 2 - 5
        img_pos_x = int(center_x - img_width  // 2)  # Size of image is 64x64
        img_pos_y = int(center_y - img_heiht // 2)  # Size of image is 64x64
        rect_x1 = int(img_pos_x - 30)
        rect_y1 = int(img_pos_y - 10)
        rect_x2 = int(img_pos_x + img_width + 30)
        rect_y2 = int(img_pos_y + img_heiht + 10)

        # create a black rectangle with white border
        copy_draw_content.rectangle((rect_x1, rect_y1, rect_x2, rect_y2), fill=(0,0,0), outline=(255,255,255), width=1)
        self.paste_image(copy_image_content ,img, (img_pos_x, img_pos_y))

        copy_draw_content.rectangle((0, rect_y2+1, self.width, self.height), fill=(0,0,0))
        # display 4 stages of the NFC process as dots
        for  i, pox in zip(range(1, 5), [-30, -10, 10, 30]):
            if i <= stage:
                copy_draw_content.ellipse((center_x + pox, rect_y2 + 6, center_x + pox + 6, rect_y2 + 12), fill=(255,255,255))
            else:
                copy_draw_content.ellipse((center_x + pox, rect_y2 + 6, center_x + pox + 6, rect_y2 + 12), fill=(0,0,0), outline=(255,255,255))
       
        if display_check:
            self.paste_image(copy_image_content, r"/app/static/icons/png_24/check-square.png", (img_pos_x, img_pos_y))
            copy_draw_content.rectangle((0, rect_y2+1, self.width, self.height), fill=(0,0,0))
            self.align_center(copy_draw_content, "Card read!", rect_y2 +10, self.font_small)
            self.oled.display(copy_image_content)
            time.sleep(3)
            self.oled.display(self.image) 
        
        if stage == 4:
            self.oled.display(self.image) 
        else:
            self.oled.display(copy_image_content)
        #self.align_center(copy_draw_content, "Terminal is locked. Press A to release", rect_y2 + 7, self.font_small)
        # self.align_center(copy_draw_content, "Press A to release", rect_y2 + 22, self.font_small)
    
    def display_message_overlay(self, message, time_to_display=5):
        # Use the currecnt image and make a copy
        copy_image_content = self.image.copy()
        copy_draw_content = ImageDraw.Draw(copy_image_content)
        # overlay a rechatngel with a lock symbol
        img = r"/app/static/icons/png_16/info-circle.png"
        img_width,  img_heiht = PIL.Image.open(img).size
        
        msg_heiht, msg_width = 25, 154
        center_x = self.width // 2
        center_y = self.height // 2 - 5
        msg_pos_x = int(center_x - msg_width  // 2)  # Size of image is 64x64
        msg_pos_y = int(center_y - msg_heiht // 2)  # Size of image is 64x64
        rect_x1 = int(msg_pos_x - 30)
        rect_y1 = int(msg_pos_y - 10)
        rect_x2 = int(msg_pos_x + msg_width + 30)
        rect_y2 = int(msg_pos_y + msg_heiht + 10)

        # the rectangle is the bound by rect_x1, rect_y1, rect_x2, rect_y2
        # calculate the position vertcal center
        img_pos_x = int(rect_x1 + (msg_heiht / 2) - (img_heiht / 2))
        img_pos_y = msg_pos_y + 2
        

        # create a black rectangle with white border
        copy_draw_content.rectangle((rect_x1, rect_y1, rect_x2, rect_y2), fill=(0,0,0), outline=(255,255,255), width=1)
        # paste the text
        self.paste_image(copy_image_content ,img, (img_pos_x, img_pos_y))
        
        warped_text = self.wrap_text(message, self.font_small, msg_pos_x, msg_width - 4 - img_width)
        for line, add_y in warped_text:
            copy_draw_content.text((img_pos_y + img_width + 10, msg_pos_y + add_y), line, font=self.font_small, fill=(255,255,255))
        
        #self.draw_text_warp(img_pos_x, img_pos_y, message, self.font_small, msg_width)
        self.oled.display(copy_image_content)
        time.sleep(time_to_display)
        self.oled.display(self.image)
    
    # =================================================================================================================
    # Text wrapping
    # =================================================================================================================
    def wrap_text(self, text, font: ImageFont.FreeTypeFont, offset, width):
        """
        Automatically wraps text to fit within the specified width.

        Args:
            draw (ImageDraw.Draw): The drawing context.
            text (str): The text to wrap.
            font (ImageFont.ImageFont): The font to use.
            offset (int): The y-axis starting position for the text.
            width (int): The maximum width in pixels for each line.

        Returns:
            list: A list of tuples, where each tuple contains the line text and its position.
        """
        lines = []  # Store the lines and their y positions
        words = text.split(' ')
        current_line = ""
        width = width - 10  
        for word in words:
            # Check the width of the current line with the new word added
            test_line = f"{current_line} {word}" if current_line else word
            # get the length of the text in pixels
            #text_width, _ = draw.textsize(test_line, font=font)
            (text_width, height), (offset_x, offset_y) = font.font.getsize(test_line)

            if text_width <= width:
                # Add the word to the current line
                current_line = test_line
            else:
                # Save the current line and start a new one
                lines.append(current_line)
                current_line = word

        # Append the last line
        if current_line:
            lines.append(current_line)

        # Calculate the y positions for each line and prepare the output
        wrapped_lines = []
        (text_width, line_height), (offset_x, offset_y) = font.font.getsize('A')
        #line_height = font.getsize("A")[1]  # Change No. #2: Replaced deprecated textsize with getsize.

        for i, line in enumerate(lines):
            y_position = i * line_height + 1
            wrapped_lines.append((line, y_position))

        return wrapped_lines

    def draw_text_warp(self, x, y, text, font, width=256, fill=(255,255,255)):
        warped_text = self.wrap_text(text, font, x, width)
        for line, add_y in warped_text:
            self.draw.text((x, y + add_y), line, font=font, fill=fill)


    # overwrite the == operator
    def __eq__(self, other):
        if other.__class__ != self.__class__:
            return False
        return self.name == other.name


    # =================================================================================================================
    # Event handling
    # =================================================================================================================
    # Actual event handeling
    def _sig_on_barcode_read(self, sender, barcode, **kwargs):
        if self.is_active:
            self.on_barcode_read(sender, barcode, **kwargs)
        
    def _sig_on_nfc_read(self, sender, id, text, **kwargs):
        if self.is_active:
            self.on_nfc_read(sender, id, text, **kwargs)

    def _sig_on_btn_pressed(self, sender, btn, **kwargs):
        if self.is_active:
            self.on_btn_pressed(sender, btn, **kwargs)

    def _sig_on_websocket_connect(self, sender, **kwargs):
        self.stores: list[Store] = list(Store.objects.filter(is_connected=True).order_by('terminal_button'))
        if self.is_active:
            self.on_websocket_connect(sender, **kwargs)

    def _sig_on_websocket_disconnect(self, sender, **kwargs):
        self.stores: list[Store] = list(Store.objects.filter(is_connected=True).order_by('terminal_button'))
        if self.is_active:
            self.on_websocket_disconnect(sender, **kwargs)

    # Need to be implemented by the subclass
    @abstractmethod
    def on_barcode_read(self, sender, barcode, **kwargs):
        pass

    @abstractmethod
    def on_nfc_read(self, sender, id, text, **kwargs):
        pass

    @abstractmethod
    def on_btn_pressed(self, sender, kypd_btn, **kwargs):
        pass

    @abstractmethod
    def on_websocket_connect(self, sender, **kwargs):
        pass    

    @abstractmethod
    def on_websocket_disconnect(self, sender, **kwargs):
        pass

    # =================================================================================================================
    # Other Helpers
    # =================================================================================================================
    def _on_barcode_read_request_products_view(self, view_controller: 'OLEDViewController',
                                                stores: list[Store], barcode: str):
        current_product = StoreProduct.get_from_api(stores, barcode)
        print(f"json: {current_product}")
        if current_product:
            view_controller.request_view(view_controller.PAGE_PRODUCT, 
                                              product=current_product)
        else:
            print(f"Product not found: {barcode}")
            view_controller.request_view(
                view_controller.PAGE_PRODUCT_UNKNW, 
                ean=barcode, 
                next_view=view_controller.PAGE_STORE_SELECTION)   
    
    def _fetch_customer(self, view_controller: 'OLEDViewController', store: StoreProduct, card_number: str):
        view_controller: OLEDViewController
        try:
            return Customer.get_from_api(store, card_number)
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            if int(e.response.json().get('code')) == 10:
                view_controller.request_view(view_controller.PAGE_CUSTOMER_UNKNW, id=card_number,
                                             # Next view handler
                                             next_view=view_controller.PAGE_MAIN,
                                             store=store)
            else:
                view_controller.request_view(view_controller.PAGE_ERROR, 
                                        error_title=f"Error {e.response.json().get('code')}", 
                                        error_message=e.response.json().get("message"),
                                        # Next view handler
                                        next_view=view_controller.PAGE_MAIN,
                                        store=store)
            return None
        
        except Exception as e:
            print(f"Error: {e}")
            view_controller.request_view(view_controller.PAGE_ERROR, 
                                        error_title="Uncought Error", error_message=f"Error processing purchase: {e}",
                                        next_view=view_controller.PAGE_MAIN,
                                        store=store)
            return None
            
    def __del__(self):
        print(f"Life of {self.name} ended.")