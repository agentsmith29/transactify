from django.apps import AppConfig
from .controller.HardwareInterface import HardwareInterface
from PIL import Image, ImageDraw, ImageFont, ImageOps
import PIL.Image
import sys

import asyncio
import websockets


from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


import json

from evdev import InputDevice, categorize, ecodes

from .models import Product, StockProductPurchase, StockProductSale, Customer, CustomerDeposit
from django.dispatch import Signal
from django.http import HttpRequest

import time



class HardwareController():


    def __init__(self, *args, **kwargs):
        print(f"HardwareController: __init__:")

        self.hwif = HardwareInterface()
        self.current_view = None #self.view_main
        self.current_products = []
        self.current_nfc = None
        
        self.hwif.barcode_reader.signals.barcode_read.connect(self.on_barcode_read)
        self.hwif.nfc_reader.signals.tag_read.connect(self.on_nfc_read)

        self.view_main()

    def on_barcode_read(self, sender, barcode, **kwargs):
        print(f"Barcode read: {barcode}")
        if self.current_view == "view_main" or self.current_view == "view_price":
            product = Product.objects.filter(ean=barcode).first()
            if product:
                self.view_price(product.name, product.resell_price)
                self.current_products.append(product)
            else:
                self.view_unknown_product()
            
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


        if self.current_view == "view_price":
            customer = Customer.objects.filter(card_number=id).first()
            print(f"Customer: {customer}")
            self.current_nfc = id
            if customer is self.current_nfc:
                print("Customer is the same")
                self.view_purchase_succesfull()
                return

            from .views import make_sale

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
    



    def view_main(self):
        
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
        header_text = f"Don Knabberello"
        draw.text((20, 1), header_text, font=font_large, fill=(255,255,255))  # Leave space for NFC symbol

        # Paste the NFC symbol into the header
        image.paste(cmd_symbol, (0, 0))  # Paste at (2, 2) in the top-left corner

        # Divider line
        draw.line([(0, header_height), (width, header_height)], fill=(255,255,255), width=1)

        # Content Section: Display Name, Surname, and Balance
        content_y_start = header_height + 5
        draw.text((30, content_y_start), f"Scan a product of your choice", font=font_small,fill=(255,255,255))

        # Update the OLED display
        self.hwif.oled.display(image)
        self.current_view = "view_main"

    def view_price(self, product_name, price):
        self.current_view = "view_price"
        # Ensure the image mode matches the display's mode
        width = self.hwif.oled.width
        height = self.hwif.oled.height
        image = Image.new(self.hwif.oled.mode, (width, height))
        draw = ImageDraw.Draw(image)
        font_extra_large = ImageFont.load_default(size=20)
        font_large = ImageFont.load_default(size=12)
        font_small = ImageFont.load_default(size=10)

        # Header Section
        header_height = 20
        header_text = f"{product_name}"
        draw.text((20, 1), header_text, font=font_large, fill=(255,255,255))  # Leave space for NFC symbol

        # Paste the NFC symbol into the header
        #image.paste(cmd_symbol, (0, 0))  # Paste at (2, 2) in the top-left corner

        # Divider line
        draw.line([(0, header_height), (width, header_height)], fill=(255,255,255), width=1)

        # Content Section: Display Name, Surname, and Balance
        content_y_start = header_height + 5
        #draw.text((30, content_y_start), f"Scan a product of your choice", font=font_small,fill=(255,255,255))
        #draw.text((30, content_y_start), f"{product_name}", font=font_large,fill=(255,255,255))
        draw.text((30, content_y_start), f"EUR {price}", font=font_extra_large,fill=(255,255,255))
        draw.text((30, content_y_start + 25), f"Press A to continue or place NFC to buy", font=font_large,fill=(255,255,255))
        # Update the OLED display
        self.hwif.oled.display(image)

    def view_unknown_product(self):
        self.current_view = "view_price"
        # Ensure the image mode matches the display's mode
        width = self.hwif.oled.width
        height = self.hwif.oled.height
        image = Image.new(self.hwif.oled.mode, (width, height))
        draw = ImageDraw.Draw(image)
        font_extra_large = ImageFont.load_default(size=20)
        font_large = ImageFont.load_default(size=12)
        font_small = ImageFont.load_default(size=10)

        # Header Section
        header_height = 20
        header_text = f"Noname"
        draw.text((20, 1), header_text, font=font_large, fill=(255,255,255))  # Leave space for NFC symbol

        # Paste the NFC symbol into the header
        #image.paste(cmd_symbol, (0, 0))  # Paste at (2, 2) in the top-left corner

        # Divider line
        draw.line([(0, header_height), (width, header_height)], fill=(255,255,255), width=1)

        # Content Section: Display Name, Surname, and Balance
        content_y_start = header_height + 5
        #draw.text((30, content_y_start), f"Scan a product of your choice", font=font_small,fill=(255,255,255))
        #draw.text((30, content_y_start), f"{product_name}", font=font_large,fill=(255,255,255))
        draw.text((30, content_y_start), f"EUR ???", font=font_extra_large,fill=(255,255,255))
        draw.text((30, content_y_start + 25), f"Place NFC to buy", font=font_large,fill=(255,255,255))
        # Update the OLED display
        self.hwif.oled.display(image)

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



    