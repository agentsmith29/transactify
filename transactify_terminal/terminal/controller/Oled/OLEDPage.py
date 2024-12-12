from django.dispatch import Signal

from PIL import Image, ImageDraw, ImageFont, ImageOps
import PIL.Image
import time


class OLEDPage():
    name: str = "OLEDPage"
    
    def __init__(self, oled, sig_abort_view: Signal, sig_request_view: Signal,
                 locked = False, overwritable = True):
        self._signal_abort_view = sig_abort_view
        self._signal_request_view = sig_request_view

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
        self.break_loop = False

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
    
    def view(self, *args, **kwargs):
        raise NotImplementedError("View not implemented")
    
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
    
    def align_center(self, draw, text, pos_y, font):
        (w, h), (offset_x, offset_y) = font.font.getsize(text)
        pos_x = (self.width - w) // 2
        pos_y = pos_y - h
        draw.text((pos_x, pos_y), text, font=font, fill=(255,255,255))    
        return w, h, pos_x, pos_y

    def display_next(self, image, draw, next_view, wait_time=20, *args, **kwargs):
            print(f"* Refreshing after {wait_time} seconds.")
            # use asyncio sleep
            for wt in range(wait_time,0,-1):
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
    
    def wrap_text(self, draw, text, font, offset, width):
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
        width = width - offset

        for word in words:
            # Check the width of the current line with the new word added
            test_line = f"{current_line} {word}" if current_line else word
            text_width, _ = draw.textsize(test_line, font=font)

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
        line_height = draw.textsize("A", font=font)[1]

        for i, line in enumerate(lines):
            y_position = offset + i * line_height
            wrapped_lines.append((line, y_position))

        return wrapped_lines



    # overwrite the == operator
    def __eq__(self, other):
        if other.__class__ != self.__class__:
            return False
        return self.name == other.name
