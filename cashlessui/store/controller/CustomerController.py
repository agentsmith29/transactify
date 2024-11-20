import sys
sys.path.append('..')

from ..models import Customer, CustomerDeposit
import asyncio
from mfrc522 import SimpleMFRC522
from controller.KeyPad import KeyPad

from luma.core.interface.serial import i2c, spi, pcf8574
from luma.core.interface.parallel import bitbang_6800
from luma.core.render import canvas
from luma.oled.device import ssd1322 as OLED

from PIL import Image, ImageDraw, ImageFont, ImageOps
import PIL.Image

from datetime import datetime

class CustomerController:
    """Encapsulates customer-related logic."""
    def __init__(self, nfc_reader: SimpleMFRC522, keypad: KeyPad, oled: OLED):
        self.reader = None #nfc_reader
        self.keypad = keypad
        self.oled = oled
        

    def view_main(self):
        oled = self.oled
        # Ensure the image mode matches the display's mode
        width = oled.width
        height = oled.height
        image = Image.new(oled.mode, (width, height))  # Use oled.mode for compatibility
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
            cmd_symbol = PIL.Image.open(r"/home/pi/workspace/cashless/cashlessui/static/icons/card-heading.png")
            cmd_symbol = cmd_symbol.convert('RGB')
            cmd_symbol = ImageOps.invert(cmd_symbol)
        except Exception as e:
            print(f"Error loading NFC symbol: {e}")
            return

        # Header Section
        header_height = 20
        header_text = f"Don Knabberello"
        draw.text((20, 1), header_text, font=font_large, fill=(255,255,255))  # Leave space for NFC symbol

        # Paste the NFC symbol into the header
        image.paste(cmd_symbol, (0, 0))  # Paste at (2, 2) in the top-left corner

        # Divider line
        draw.line([(0, header_height), (width, header_height)], fill=(255,255,255), width=1)

        # Content Section: Display Name, Surname, and Balance
        content_y_start = header_height + 5
        draw.text((30, content_y_start), f"Welcome. Please scan the product of interest.", font=font_small,fill=(255,255,255))
        # inster spinner here

        # Update the OLED display
        oled.display(image)
    
    def view_present_card_old(self, surname, name, balance):
        with canvas(self.oled) as draw:
            draw.rectangle(self.oled.bounding_box, outline="white", fill="black")
            draw.text((30, 10), f"Surname: {surname}", fill="white")
            draw.text((30, 20), f"Name: {name}", fill="white")
            draw.text((30, 30), f"Balance: {balance}", fill="white")
            draw.text((30, 40), f"Present card or input access code", fill="white")

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
        oled = self.oled
        # Ensure the image mode matches the display's mode
        width = oled.width
        height = oled.height
        image = Image.new(oled.mode, (width, height))  # Use oled.mode for compatibility
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
            cmd_symbol = PIL.Image.open(r"/home/pi/workspace/cashless/cashlessui/static/icons/card-heading.png")
            cmd_symbol = cmd_symbol.convert('RGB')
            cmd_symbol = ImageOps.invert(cmd_symbol)

            nfc_symbol = PIL.Image.open(r"/home/pi/workspace/cashless/cashlessui/static/icons/rss_24_24.png")
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

        # save the image
        image.save("new_customer.png")

        # Update the OLED display
        oled.display(image)


    def nfc_read(self):
        """Simulates an NFC read."""
        #loop = asyncio.get_event_loop()
        #id, text = await loop.run_in_executor(None, self.reader.read)
        id, text = self.reader.read()
        return id, text
    
    async def nfc_write(self, text):
        """Simulates an NFC write."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.reader.write, text)

    def create_customer(self,name, surname, balance, card_number):
        """Creates and saves a new customer."""
        customer = Customer.objects.create(
            card_number=card_number,
            name=name,  
            surname=surname,
            balance=balance
        )
        deposit = CustomerDeposit.objects.create(
            customer=customer,
            amount=balance,
            timestamp=datetime.now()
        )
        return customer

    def get_all_customers(self):
        """Returns all customers."""
        return Customer.objects.all()
