from .OLEDPage import OLEDPage
from .OLEDMainPage import OLEDPageMain
from .OLEDPageProduct import OLEDPageProduct
from .OLEDPageManageProducts import OLEDPageProducts_Manage
from .OLEDPageUnknownProduct import OLEDPageProduct_Unknown

from .OLEDPageCustomer import OLEDPageCustomer
from .OLEDPageCustomerUnknown import OLEDPageCustomer_Unknown
from .OLEDPagePurchaseSuccessfull import OLEDPagePurchaseSuccessfull

from .OLEDPageInsufficientStock import OLEDPageInsufficientStock


from django.dispatch import Signal

from PIL import Image, ImageDraw, ImageFont, ImageOps
import PIL.Image

import asyncio


import time
import os
import threading

#from ...webmodels.StoreProduct import StoreProduct
#from cashlessui.models import Customer

class OLEDView():

    
    def __init__(self, oled):
        self.sig_abort_page = Signal()
        self.sig_request_view = Signal()
        self.sig_request_view.connect(self.request_view)

        self.PAGE_MAIN = OLEDPageMain(oled, self.sig_abort_page, self.sig_request_view)

        self.PAGE_INSUFF_STOCK = OLEDPageInsufficientStock(oled, self.sig_abort_page, self.sig_request_view)
        
        self.PAGE_PRODUCT = OLEDPageProduct(oled, self.sig_abort_page, self.sig_request_view)
        self.PAGE_PRODUCT_UNKNW = OLEDPageProduct_Unknown(oled, self.sig_abort_page, self.sig_request_view)
        self.PAGE_PRODUCTS_MGM = OLEDPageProducts_Manage(oled, self.sig_abort_page, self.sig_request_view)
        
        
        self.PAGE_CUSTOMER = OLEDPageCustomer(oled, self.sig_abort_page, self.sig_request_view)
        self.PAGE_CUSTOMER_UNKNW = OLEDPageCustomer_Unknown(oled, self.sig_abort_page, self.sig_request_view)

        self.PAGE_PURCHASE_SUCC = OLEDPagePurchaseSuccessfull(oled, self.sig_abort_page, self.sig_request_view)

        self.oled = oled
        
        # Some view flag handeling
        # Stores the current view. Needed, to allow the controller to respond differently to events
        self.current_view: OLEDPage = None 
        
        #try:
        #    self.loop = asyncio.get_running_loop()
        #except RuntimeError:
        #    self.loop = asyncio.new_event_loop()
        #    asyncio.set_event_loop(self.loop)
        #self.executor = ThreadPoolExecutor()
        #self.return_to_view_timer = None
        #self.return_to_view_event_loop = asyncio.new_event_loop()
        self.view_thread = None
        self.break_loop = False

        # Flags
        self.button_A_for_release = False   # Allows the release of the terminal by pressing button A

   
    # =========================================================================================================================================
    # Wrapper with parameter name and releasable
    # =========================================================================================================================================
    def oled_view_wrapper(view_function, name=None, locked=False, releasable=False):
        """
        Wrapper function for OLED views to add parameters: name, locked, and releasable.

        Args:
            view_function (callable): The OLED rendering function to wrap.
            name (str): Optional name for the view.
            locked (bool): Whether the view is locked.
            releasable (bool): Whether the locked view can be accessed.

        Returns:
            callable: The wrapped view function.
        """
        def wrapped_view(*args, **kwargs):
            # If the view is locked and not releasable, exit early
            if locked and not releasable:
                print(f"View '{name}' is locked and not releasable. Exiting.")
                return

            # Log view access
            print(f"Rendering OLED view: {name or 'Unnamed View'}")

            # Execute the actual OLED rendering function
            return view_function(*args, **kwargs)

        # Attach metadata to the wrapped function
        wrapped_view.name = name
        wrapped_view.locked = locked
        wrapped_view.releasable = releasable

        return wrapped_view

    
    def request_view(self, view: OLEDPage | str, unlock=False, *args, **kwargs): 
        # if given a string for the view, get the view object.
        if self.current_view is not None and self.current_view.locked and not unlock:
            print(f"View {self.current_view.name} is locked. Exiting.")
            return
        
        view_found = False
        for attr in dir(self):
            attr = getattr(self, attr)
            if isinstance(view, str) and attr.name == view:
                view = attr
                break
            elif not isinstance(view, str) and isinstance(attr, OLEDPage) and attr.name == view.class_name():
                view = attr
                break
       

        print(f"Requesting view: {view}.")
        if self.view_thread is not None and self.view_thread.is_alive():
            try:
                self.view_thread.join() 
            except Exception as e:
                print(f"Error joining thread: {e}")
        self.current_view = view
        self.view_thread = threading.Thread(target=view.view, args=args, kwargs=kwargs, daemon=True)
        self.view_thread.start()
        #()   


    # =========================================================================================================================================
    # Old functions
    # TODO: Delete
    # =========================================================================================================================================

    def customer_info(self, customer):
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
