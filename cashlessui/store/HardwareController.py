from django.apps import AppConfig
from .controller.HardwareInterface import HardwareInterface
from PIL import Image, ImageDraw, ImageFont, ImageOps
import PIL.Image
import sys

import asyncio
import websockets
import serial

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

import threading
import json

from evdev import InputDevice, categorize, ecodes

from .models import Product, StockProductPurchase, StockProductSale, Customer, CustomerDeposit

class HardwareController():


    def __init__(self, *args, **kwargs):
        print(f"HardwareController: __init__:")
        self.hwif = HardwareInterface()
        self.current_view = None#self.view_main

        self.view_main()

        
        
        scanner_thread  = threading.Thread(target=self.read_barcode_stdin, daemon=True)
        scanner_thread.start()

    def nfc_read(self):
        """Simulates an NFC read."""
        #loop = asyncio.get_event_loop()
        #id, text = await loop.run_in_executor(None, self.reader.read)
        id, text = self.reader.read()
        return id, text
    
    def nfc_write(self, text):
        """Simulates an NFC write."""
        #loop = asyncio.get_event_loop()
        #await loop.run_in_executor(None, self.reader.write, text)
        self.reader.write(text)

    def send_message_to_manage_clients(barcode):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "page_manage_products",  # Group name for "manage_clients"
            {
                "type": "page_message",
                "message": f"New scanned barcode: {barcode}",
                "barcode": barcode,
            },
        )
    
    # Define the threaded function to read barcodes and broadcast them
    def read_barcodes():
        # Open the serial connection
        try:
            ser = serial.Serial('/dev/ttyACM0', 19200, timeout=1)  # Adjust the port and baud rate
            print("Serial connection established")
        except serial.SerialException as e:
            print(f"Error connecting to serial port: {e}")
            return

        buffer = ""  # Temporary storage for incoming data

        while True:
            try:
                # Read raw bytes from the serial port
                raw_data = ser.read(ser.in_waiting or 1).decode('utf-8')
                if raw_data:
                    buffer += raw_data  # Append incoming data to the buffer
                    
                    # Process lines if CR or LF is received
                    while '\n' in buffer or '\r' in buffer:
                        line, buffer = buffer.splitlines(1)  # Extract the first complete line
                        line = line.strip()  # Remove leading/trailing whitespace
                        
                        if line:  # Ensure the line is not empty
                            print(f"Received complete barcode: {line}")
                            HardwareController.send_message_to_manage_clients(line)

            except serial.SerialException as e:
                print(f"Serial error: {e}")
                #break  # Exit if there's a serial connection issue

            except Exception as e:
                print(f"Error processing data: {e}")

    def read_barcode_stdin(self):
        try:
            # Open the HID device
            device = InputDevice('/dev/input/event4')  # Adjust the event number
            #print(f"Listening for barcodes on {device.name} ({hid_device_path})")

            barcode = ""  # Buffer for building the barcode
            key_pressed = False  # Track if a key is currently pressed

            # Loop to read events
            for event in device.read_loop():
                if event.type == ecodes.EV_KEY:  # Only process key events
                    key_event = categorize(event)

                    if key_event.keystate == key_event.key_down and not key_pressed:
                        # Process the key only if no key is currently pressed
                        #print(f"Key: {key_event.keycode}")
                        key_pressed = True
                        key = key_event.keycode

                        if key == "KEY_ENTER":  # Barcode ends with Enter
                            if barcode:  # Only process if buffer is not empty
                                print(f"Received barcode: {barcode}")
                                if self.current_view == "view_main":
                                    # Get the product name and price from the database
                                    try:
                                        product = Product.objects.filter(ean=barcode).first()
                                        self.view_price(product.name, product.resell_price)
                                    except Exception as e:
                                        print(f"Error fetching product: {e}")
                                else:
                                    print(f"Barcode received, but not in the main view {self.current_view}")
                                    HardwareController.send_message_to_manage_clients(barcode)  # Send barcode
                                barcode = ""  # Reset buffer
                        elif key.startswith("KEY_") and len(key) > 4:
                            if key == "KEY_NUMLOCK" or key == "KEY_DOWN":
                                continue
                            else:
                                print(f"Key: {key}")
                            # Map keys to characters (e.g., KEY_1 -> '1')
                            char = key[-1] if key[-1].isdigit() else key[-1].lower()
                            barcode += char

                    elif key_event.keystate == key_event.key_up:
                        # Reset the key_pressed state on key release
                        key_pressed = False

        except KeyboardInterrupt:
            print("\nStopping barcode reader...")
        except Exception as e:
            print(f"Error: {e}")

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
        draw.text((30, content_y_start), f"Scan a product of your choice", font=font_small,fill=(255,255,255))

        # Update the OLED display
        self.hwif.oled.display(image)
        self.current_view = "view_main"


    def view_price(self, product_name = "", price = ""):
        self.current_view = self.view_price
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
        header_text = f"Produktabfrage"
        draw.text((20, 1), header_text, font=font_large, fill=(255,255,255))  # Leave space for NFC symbol

        # Paste the NFC symbol into the header
        #image.paste(cmd_symbol, (0, 0))  # Paste at (2, 2) in the top-left corner

        # Divider line
        draw.line([(0, header_height), (width, header_height)], fill=(255,255,255), width=1)

        # Content Section: Display Name, Surname, and Balance
        content_y_start = header_height + 5
        #draw.text((30, content_y_start), f"Scan a product of your choice", font=font_small,fill=(255,255,255))
        draw.text((30, content_y_start), f"{product_name}", font=font_large,fill=(255,255,255))
        draw.text((30, content_y_start + 15), f"EUR {price}", font=font_extra_large,fill=(255,255,255))
        # Update the OLED display
        self.hwif.oled.display(image)



    