from django.apps import AppConfig
from .HardwareInterface import HardwareInterface
from PIL import Image, ImageDraw, ImageFont, ImageOps
import PIL.Image
import sys

import asyncio
import websockets


from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from concurrent.futures import ThreadPoolExecutor

import json

from evdev import InputDevice, categorize, ecodes

from ..webmodels.StoreProduct import StoreProduct
from cashlessui.models import Customer
from django.dispatch import Signal
from django.http import HttpRequest

import time
import os
import threading


class HardwareController():
    init_counter = 0

    def __init__(self, *args, **kwargs):
        print(f"HardwareController: __init__: {HardwareController.init_counter}")
        HardwareController.init_counter += 1

        lock_interaction = False

        self.hwif = HardwareInterface()
        self.current_view = None #self.view_main
        self.current_products = []
        
        self.hwif.barcode_reader.signals.barcode_read.connect(self.on_barcode_read)
        self.hwif.nfc_reader.signals.tag_read.connect(self.on_nfc_read)
        self.hwif.keypad.signals.key_pressed.connect(self.on_key_pressed)




        self.view = OLEDView(self.hwif.oled)
        self.view.request_view(self.view.view_main)


    def lock_hardware(self):
        lock_interaction = True

    def on_key_pressed(self, sender, col, row, btn, **kwargs):
        if self.view.current_view == "view_start_product_management":
            if self.view.button_A_for_release and btn == "A":
                self.view.request_view(self.view.view_main)

    def on_barcode_read(self, sender, barcode, **kwargs):
        print(f"Barcode read: {barcode}")
        if self.view.current_view == "view_main" or self.current_view == "view_price":
            product = StoreProduct.objects.filter(ean=barcode).first()
            if product:
                self.view.request_view(self.view.view_price, product.name, product.resell_price)
                self.current_products.append(product)
            else:
                self.view.request_view(self.view.view_unknown_product, barcode)
        else:
            print(f"Barcode read, but no view to handle it: {self.current_view}")
        self.send_message_to_page(
            "page_manage_products",
            {
                "type": "page_message",
                "message": f"New scanned barcode: {barcode}",
                "barcode": barcode,
            }
        )
        # self.view_price(barcode)
        # self.view_main()
        
    def on_nfc_read(self, sender, id, text, **kwargs):
        print(f"NFC read {id}: {text}")
        if self.view.current_view == "view_main":
            print(Customer.objects.all())
            customer = Customer.objects.get(card_number=id)
            if customer:
                self.view.request_view(self.view.customer_info, customer)
            else:
                 self.view.request_view(self.view.unknown_card)
        elif self.current_view == "view_price":
            customer = Customer.objects.filter(card_number=id).first()
            print(f"Customer: {customer}")
            self.current_nfc = id
            if customer is self.current_nfc:
                print("Customer is the same")
                self.view_purchase_succesfull()
                return

            from ..views import make_sale

            # Iterate through the current products and create a simulated HTTP POST request
            for p in self.current_products:
                request = HttpRequest()
                request.method = 'POST'
                request.POST = {
                    'ean': p.ean,
                    'quantity': 1,
                    'sale_price': str(p.resell_price),  # Ensure the price is a string for POST
                    'customer': customer # Use customer ID
                }

                # Call the make_sale function
                response = make_sale(request)
                print("Sold product!")

                # Optionally handle the response if needed
                print(response.status_code, response.content)
                self.view_purchase_succesfull()

        elif self.current_view == "view_start_card_management":
            self.send_message_to_page(
                "page_view_customers",
                {
                    "type": "page_message",
                    "message": f"New scanned card: {id}",
                    "card_id": id,
                    "text": text,

                }
            )
    
    def nfc_write(self, text):
        """Simulates an NFC write."""
        #loop = asyncio.get_event_loop()
        #await loop.run_in_executor(None, self.reader.write, text)
        self.hwif.nfc_reader.write(text)

    def send_message_to_page(self, page, payload):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            page, 
            payload,
        )
    

class OLEDView():

    def __init__(self, oled):
        self.oled = oled
        self.current_view = None   

        self.width = self.oled.width
        self.height = self.oled.height

        self.font_large = ImageFont.load_default(size=16)
        self.font_regular = ImageFont.load_default(size=12)
        self.font_small = ImageFont.load_default(size=10)
        self.font_tiny = ImageFont.load_default(size=8)
        
        #try:
        #    self.loop = asyncio.get_running_loop()
        #except RuntimeError:
        #    self.loop = asyncio.new_event_loop()
        #    asyncio.set_event_loop(self.loop)
        #self.executor = ThreadPoolExecutor()
        #self.return_to_view_timer = None
        #self.return_to_view_event_loop = asyncio.new_event_loop()
        self.scanner_thread = None
        self.break_loop = False

        # Flags
        self.button_A_for_release = False   # Allows the release of the terminal by pressing button A

    def request_view(self, view, *args, **kwargs): 
        print(f"Requesting view: {view}.")
        self.break_loop = True 
        if self.scanner_thread is not None and self.scanner_thread.is_alive():
            try:
                self.scanner_thread.join() 
            except Exception as e:
                print(f"Error joining thread: {e}")
        self.break_loop = False

        self.scanner_thread = threading.Thread(target=view, args=args, kwargs=kwargs, daemon=True)
        self.scanner_thread.start()
        #()   

    def paste_image(self, image, path, pos):
        try:
            symb = PIL.Image.open(path)
            symb = symb.convert('RGB')
            symb = ImageOps.invert(symb)
            image.paste(symb, pos)  # Paste at (2, 2) in the top-left corner
        except Exception as e:
            print(f"Error loading symbol: {e}")

    def align_right(self, draw, text, pos_y, font):
        (w, h), (offset_x, offset_y) = font.font.getsize(text)
        pos_x = self.width - w
        pos_y = pos_y - h
        draw.text((pos_x, pos_y), text, font=font, fill=(255,255,255))    
        return w, h, pos_x, pos_y
    
    def display_next(self, image, draw, next_view, wait_time=20):
            print(f"* Refreshing after {wait_time} seconds.")
            # use asyncio sleep
            for wt in range(wait_time,0,-1):
                print(f"Break loop? {self.break_loop}")
                if self.break_loop:
                    print("Break loop")
                    return
                #await asyncio.sleep(1)
                time.sleep(1)
                segment = int((self.width / wait_time) * wt)
                draw.line([(0, 20), (segment, 20)], fill=(255, 255, 255), width=1)
                draw.line([(segment, 20), (self.width, 20)], fill=(0,0,0), width=1)
                #draw.rectangle((pos_x-w, pos_y-y, pos_x + w, pos_y + h), fill="black")
                #w, h, pos_x, pos_y = self.align_right(draw, str(wt), 10, self.font_small)
                # clear the display w, h, pos_x, pos_y 
                print(f"> Displaying next view in {wt} seconds.", end="\r")
                # print inline the countdown, no new line

                self.oled.display(image)
            self.request_view(next_view)

    async def display_nexto(self, image, draw, next_view, wait_time=20):
        try:
            for wt in range(wait_time, 0, -1):
                segment = int((self.width / wait_time) * wt)
                draw.line([(0, 20), (segment, 20)], fill=(255, 255, 255), width=1)
                draw.line([(segment, 20), (self.width, 20)], fill=(0, 0, 0), width=1)
                
                print(f"Displaying next view in {wt} seconds.")
                self.oled.display(image)

                # Use asyncio sleep instead of time.sleep
                await asyncio.sleep(1)
            # When the countdown completes, request the next view
            self.request_view(next_view)
        except asyncio.CancelledError:
            print("Countdown cancelled.")
            # Optional: Clear the display if cancelled
            draw.rectangle((0, 0, self.width, self.height), fill=(0, 0, 0))
            self.oled.display(image)
    
    # =========================================================================================================================================
    # Views
    # =========================================================================================================================================

    def view_main(self):
        self.current_view = "view_main"
        # clear the display
        image = Image.new(self.oled.mode, (self.width, self.height))  # Use oled.mode for compatibility
        draw = ImageDraw.Draw(image)  
        # Header Section
        header_height = 20
        header_text = f"Don Knabberello"
        draw.text((20, 0), header_text, font=self.font_large, fill=(255,255,255))  # Leave space for NFC symbol

        ip_address = f"{os.getenv('DJANGO_WEB_HOST')}:{os.getenv('DJANGO_WEB_PORT')}"
        self.align_right(draw, ip_address, 10, self.font_tiny)
        # Paste the NFC symbol into the header
        self.paste_image(image, r"/app/static/icons/png_16/coin.png", (0, 0))
        # Divider line
        draw.line([(0, header_height), (self.width, header_height)], fill=(255,255,255), width=1)

        # ------------- Body ----------------
        # Content Section: Display Name, Surname, and Balance
        content_y_start = header_height + 5
        draw.text((30, content_y_start), f"Scan a product of your choice", font=self.font_small, fill=(255,255,255))
       
        # Update the OLED display
        self.oled.display(image)
        # ------------- Body ----------------


    def view_price(self, product_name, price):
        self.current_view = "view_price"

        image = Image.new(self.oled.mode, (self.width, self.height))  # Use oled.mode for compatibility
        draw = ImageDraw.Draw(image)  

        # Header Section
        header_height = 20
        header_text = f"{product_name}"
        draw.text((20, 0), header_text, font=self.font_large, fill=(255,255,255))  # Leave space for NFC symbol

        # Paste the NFC symbol into the header
        self.paste_image(image, r"/app/static/icons/png_16/cart-dash-fill.png", (0, 0))

        # Divider line
        draw.line([(0, header_height), (self.width, header_height)], fill=(255,255,255), width=1)

        content_y_start = header_height + 5
        draw.text((30, content_y_start), f"EUR {price}", font=self.font_large,fill=(255,255,255))
        draw.text((30, content_y_start + 25), f"Press A to continue or place NFC to buy", font=self.font_regular, fill=(255,255,255))
        # Update the OLED display
        self.oled.display(image)

        #fnkt = lambda: self.display_next(image, draw, self.view_main, 20)
        #self.return_to_view_timer = self.return_to_view_event_loop.run_in_executor(None, fnkt)
        self.display_next(image, draw, self.view_main, 20)
        #self.return_to_view_timer = self.loop.run_in_executor(self.executor, fnkt)

    def view_unknown_product(self, ean):
        self.current_view = "view_price"
        # Ensure the image mode matches the display's mode
        width = self.oled.width
        height = self.oled.height
        image = Image.new(self.oled.mode, (width, height))
        draw = ImageDraw.Draw(image)
        font_large = ImageFont.load_default(size=20)
        font_regular = ImageFont.load_default(size=12)
        font_small = ImageFont.load_default(size=10)

        # Header Section
        header_height = 20
        header_text = f"Unknown Product `{ean}`"
        draw.text((20, 1), header_text, font=font_regular, fill=(255,255,255))  # Leave space for NFC symbol

        # Paste the NFC symbol into the header
        #image.paste(cmd_symbol, (0, 0))  # Paste at (2, 2) in the top-left corner

        # Divider line
        draw.line([(0, header_height), (width, header_height)], fill=(255,255,255), width=1)

        # Content Section: Display Name, Surname, and Balance
        content_y_start = header_height + 4
        #draw.text((30, content_y_start), f"Scan a product of your choice", font=font_small,fill=(255,255,255))
        #draw.text((30, content_y_start), f"{product_name}", font=font_large,fill=(255,255,255))
        ip_address = f"{os.getenv('DJANGO_WEB_HOST')}:{os.getenv('DJANGO_WEB_PORT')}"
        draw.text((10, content_y_start), f"The scanned poduct was not found in the database.", font=font_small,fill=(255,255,255))
        draw.text((10, content_y_start + 14), f"Please add it using the webinterface under", font=font_small,fill=(255,255,255))
        draw.text((10, content_y_start + 28), f"{ip_address}", font=font_small,fill=(255,255,255))
        # Update the OLED display
        self.hwif.oled.display(image)

         # start a asynchrounous timer
        asynytimer = asyncio.new_event_loop()
        def display_main():
            time.sleep(10)
            self.view_main()
        asynytimer.run_in_executor(None, display_main)


    def customer_info(self, customer: Customer):
        self.current_view = "customer_info"
        # Ensure the image mode matches the display's mode
        image = Image.new(self.oled.mode, (self.width, self.height))  # Use oled.mode for compatibility
        draw = ImageDraw.Draw(image)  
        # Header Section
        header_height = 20
        header_text = f"Hello, {customer.user.first_name} {customer.user.last_name}"
        draw.text((20, 0), header_text, font=self.font_large, fill=(255,255,255))  # Leave space for NFC symbol


       
        self.paste_image(image, r"/app/static/icons/png_16/person-bounding-box.png", (0, 0))
        # Divider line
        draw.line([(0, header_height), (self.width, header_height)], fill=(255,255,255), width=1)

        # ------------- Body ----------------
        # Content Section: Display Name, Surname, and Balance
        content_y_start = header_height + 5
        self.paste_image(image, r"/app/static/icons/png_16/cash-stack.png", (0, content_y_start))
        draw.text((30, content_y_start+2), f"Balance: EUR:", font=self.font_regular, fill=(255,255,255))
        self.paste_image(image, r"/app/static/icons/png_16/cart4.png", (0, content_y_start+18))
        draw.text((30, content_y_start+20), f"Last purchase: ", font=self.font_regular, fill=(255,255,255))

        # Update the OLED display
        self.oled.display(image)
        # ------------- Body ----------------
        self.display_next(image, draw, self.view_main, 20)

    def unknown_card(self):
        self.current_view = "customer_unknown"
        # Ensure the image mode matches the display's mode
        image = Image.new(self.oled.mode, (self.width, self.height))  # Use oled.mode for compatibility
        draw = ImageDraw.Draw(image)  
        # Header Section
        header_height = 20
        header_text = f"Unknown Card"
        draw.text((20, 0), header_text, font=self.font_large, fill=(255,255,255))  # Leave space for NFC symbol


       
        self.paste_image(image, r"/app/static/icons/png_16/person-fill-x.png", (0, 0))
        # Divider line
        draw.line([(0, header_height), (self.width, header_height)], fill=(255,255,255), width=1)

        # ------------- Body ----------------
        # Content Section: Display Name, Surname, and Balance
        self.paste_image(image, r"/app/static/icons/png_24/person-fill-x.png", (0, content_y_start))
        content_y_start = header_height + 5
        draw.text((30, content_y_start+2), f"Card is unknown or not bind to a customer.", font=self.font_regular, fill=(255,255,255))

        # Update the OLED display
        self.oled.display(image)
        # ------------- Body ----------------
        self.display_next(image, draw, self.view_main, 20)


    def view_purchase_succesfull(self):
        self.current_view = "view_purchase_succesfull"
        # Ensure the image mode matches the display's mode
        width = self.hwif.oled.width
        height = self.hwif.oled.height
        image = Image.new(self.hwif.oled.mode, (width, height))
        draw = ImageDraw.Draw(image)
        font_extra_large = ImageFont.load_default(size=20)
        font_large = ImageFont.load_default(size=12)
        font_small = ImageFont.load_default(size=10)

        try:
            cmd_symbol = PIL.Image.open(r"/app/static/icons/png_16/cart-check-fill.png")
            cmd_symbol = cmd_symbol.convert('RGB')
            cmd_symbol = ImageOps.invert(cmd_symbol)
            image.paste(cmd_symbol, (0, 0))  # Paste at (2, 2) in the top-left corner
        except Exception as e:
            print(f"Error loading NFC symbol: {e}")
        

        # Header Section
        header_height = 20
        header_text = f"Success"
        draw.text((20, 1), header_text, font=font_large, fill=(255,255,255))

        # thank you for your purchase
        # Divider line
        draw.line([(0, header_height), (width, header_height)], fill=(255,255,255), width=1)
        draw.text((30, 40), f"Thank you for your purchase!", font=font_large,fill=(255,255,255))

        self.hwif.oled.display(image)



    def view_start_card_management(self):
        self.current_view = "view_start_card_management"
        # Ensure the image mode matches the display's mode
        width = self.hwif.oled.width
        height = self.hwif.oled.height
        image = Image.new(self.hwif.oled.mode, (width, height))  # Use oled.mode for compatibility
        draw = ImageDraw.Draw(image)

        font_large = ImageFont.load_default(size=12)
        font_small = ImageFont.load_default(size=10)

        # Load and resize the NFC symbol image
        try:
            cmd_symbol = PIL.Image.open(r"/app/static/icons/card-heading.png")
            cmd_symbol = cmd_symbol.convert('RGB')
            cmd_symbol = ImageOps.invert(cmd_symbol)
        except Exception as e:
            print(f"Error loading NFC symbol: {e}")
            return

        # Header Section
        header_height = 20
        header_text = f"Card Management"
        draw.text((20, 1), header_text, font=font_large, fill=(255,255,255))  # Leave space for NFC symbol

        # Paste the NFC symbol into the header
        image.paste(cmd_symbol, (0, 0))  # Paste at (2, 2) in the top-left corner

        # Divider line
        draw.line([(0, header_height), (width, header_height)], fill=(255,255,255), width=1)

        # Content Section: Display Name, Surname, and Balance
        content_y_start = header_height + 5
        draw.text((30, content_y_start), f"A new card is in preperation. Please wait.", font=font_small,fill=(255,255,255))
        # inster spinner here

        # Update the OLED display
        self.hwif.oled.display(image)

        # start a asynchrounous timer
        asynytimer = asyncio.new_event_loop()
        def display_main():
            time.sleep(5)
            self.view_main()
        asynytimer.run_in_executor(None, display_main)

    def view_present_card(self, name, surname, balance):
        """
        Display information for issuing a new customer card on a 256x64 OLED.

        Args:
            oled: The initialized OLED display object from luma.oled.device.
            name: Customer's first name.
            surname: Customer's last name.
            balance: Customer's account balance.
            nfc_symbol_path: Path to the NFC symbol image.
        """
        #oled = hwcontroller.hwif.oled
        # Ensure the image mode matches the display's mode
        width = self.hwif.oled.width
        height = self.hwif.oled.height
        image = Image.new(self.hwif.oled.mode, (width, height))  # Use oled.mode for compatibility
        draw = ImageDraw.Draw(image)

        # Load fonts (adjust paths and sizes as necessary)
        #try:
        #font_large = ImageFont.truetype("arial.ttf", 18)  # Large font for titles
        #font_small = ImageFont.truetype("arial.ttf", 14)  # Smaller font for details
        #except IOError:
        font_large = ImageFont.load_default(size=12)
        font_small = ImageFont.load_default(size=10)

        # Load and resize the NFC symbol image
        try:
            cmd_symbol = PIL.Image.open(r"/app/static/icons/card-heading.png")
            cmd_symbol = cmd_symbol.convert('RGB')
            cmd_symbol = ImageOps.invert(cmd_symbol)

            nfc_symbol = PIL.Image.open(r"/app/static/icons/rss_24_24.png")
            nfc_symbol = nfc_symbol.convert('RGB')
            nfc_symbol = ImageOps.invert(nfc_symbol)
            #nfc_symbol = nfc_symbol.resize((20, 20))  # Resize the symbol to fit the header
        except Exception as e:
            print(f"Error loading NFC symbol: {e}")
            return

        # Header Section
        header_height = 20
        header_text = f"Issue new Card"
        draw.text((20, 1), header_text, font=font_large, fill=(255,255,255))  # Leave space for NFC symbol

        # Paste the NFC symbol into the header
        image.paste(cmd_symbol, (0, 0))  # Paste at (2, 2) in the top-left corner

        # Divider line
        draw.line([(0, header_height), (width, header_height)], fill=(255,255,255), width=1)

        # Content Section: Display Name, Surname, and Balance
        content_y_start = header_height + 5
        draw.text((30, content_y_start), f"Issue new card for: {name} {surname}", font=font_small,fill=(255,255,255))
        draw.text((30, content_y_start + 12), f"Initial balance: EUR {float(balance):.2f}", font=font_small, fill=(255,255,255))
        draw.text((30, content_y_start + 22), f"Please place your card now.", font=font_small, fill=(255,255,255))
        image.paste(nfc_symbol, (2, content_y_start+5))  # Paste at (2, 2) in the top-left corner

        # Draw NFC readiness indication
        nfc_ready_text = "Tap card on NFC reader..."
        draw.text((160, content_y_start + 40), nfc_ready_text, font=font_small, fill=(255,255,255))

        # Update the OLED display
        self.hwif.oled.display(image)



    