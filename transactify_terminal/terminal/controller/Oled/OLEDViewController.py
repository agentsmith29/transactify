from .OLEDStoreSelection import OLEDStoreSelection
from .OLEDPage import OLEDPage
from .OLEDPageStoreMain import OLEDPageStoreMain
from .OLEDPageProduct import OLEDPageProduct
from .OLEDPageManageProducts import OLEDPageProducts_Manage
from .OLEDPageUnknownProduct import OLEDPageProduct_Unknown

from .OLEDPageCustomer import OLEDPageCustomer
from .OLEDPageCustomerUnknown import OLEDPageCustomer_Unknown
from .OLEDPagePurchaseSuccessfull import OLEDPagePurchaseSuccessfull

from .OLEDScreenSaver import OLEDScreenSaver

from .OLEDPageInsufficientStock import OLEDPageInsufficientStock

from .OLEDPageError import OLEDPageError


from django.dispatch import Signal

from PIL import Image, ImageDraw, ImageFont, ImageOps
import PIL.Image

import asyncio


import time
import os
import threading


from ..ConfParser import Store
from ...api_endpoints.StoreProduct import StoreProduct
from luma.oled.device import ssd1322 as OLED
#from luma.lcd.device import ili9341 as OLED

from ..LEDStripController import LEDStripController

class OLEDViewControllerSignals():
    view_changed = Signal()


class OLEDViewController():
    OLED_SCREEN_SAVER_TIMEOUT = 5
    
    def __init__(self, oled: OLED,
                 sig_on_barcode_read: Signal,
                 sig_on_nfc_read: Signal,
                 sig_on_btn_pressed: Signal,
                 stores: list[Store],
                 ledstrip: LEDStripController):
        
        self.sig_abort_page = Signal()
        self.sig_request_view = Signal()
        self.sig_request_view.connect(self.request_view)
        self.oled = oled
        self.ledstrip = ledstrip

        self.signals = OLEDViewControllerSignals()

        kwargs = {
            "oled": oled, 'stores': stores,
            'view_controller': self,
            "sig_abort_view": self.sig_abort_page,
            "sig_request_view": self.sig_request_view,
            #
            "sig_on_barcode_read": sig_on_barcode_read,
            "sig_on_nfc_read": sig_on_nfc_read,
            "sig_on_btn_pressed": sig_on_btn_pressed,
            "ledstrip": ledstrip
        }

        self.PAGE_STORE_SELECTION = OLEDStoreSelection(**kwargs)

        self.PAGE_MAIN = OLEDPageStoreMain(**kwargs)
        
        self.PAGE_INSUFF_STOCK = OLEDPageInsufficientStock(**kwargs)
        self.PAGE_PRODUCT = OLEDPageProduct(**kwargs)
        self.PAGE_PRODUCT_UNKNW = OLEDPageProduct_Unknown(**kwargs)
        self.PAGE_PRODUCTS_MGM = OLEDPageProducts_Manage(**kwargs)
        
        
        self.PAGE_CUSTOMER = OLEDPageCustomer(**kwargs)
        self.PAGE_CUSTOMER_UNKNW = OLEDPageCustomer_Unknown(**kwargs)
        self.PAGE_PURCHASE_SUCC = OLEDPagePurchaseSuccessfull(**kwargs)
        self.PAGE_ERROR = OLEDPageError(**kwargs)

        self._SCREEN_SAVER = OLEDScreenSaver(**kwargs)

        
        
        # Stores the current view. Needed, to allow the controller to respond differently to events
        self.current_view: OLEDPage = None 
    

        self.view_thread = None
        self.break_loop = False

        # Flags
        self.button_A_for_release = False   # Allows the release of the terminal by pressing button A

        
        self._screensaver_timeout = OLEDViewController.OLED_SCREEN_SAVER_TIMEOUT
        self._screensaver_time_left = self._screensaver_timeout 

        self._init_screensaver_thread()

        sig_on_barcode_read.connect(self.on_barcode_read)
        sig_on_nfc_read.connect(self.on_nfc_read)
        sig_on_btn_pressed.connect(self.on_btn_pressed)
    
    def on_barcode_read(self, sender, barcode, **kwargs):
        self._reset_screensaver_timer()

    def on_nfc_read(self, sender, nfc, **kwargs):
        self._reset_screensaver_timer()
        
    def on_btn_pressed(self, sender, btn, **kwargs):
        self._reset_screensaver_timer()

    # =========================================================================================================================================
    # Screensaver Timer
    # =========================================================================================================================================
    def _init_screensaver_thread(self):
        """
        Initialize the screensaver thread.
        """
        self.screensaver_thread = threading.Thread(target=self._screensaver_timer, 
                                                    args=(self._screensaver_timeout,), daemon=True)
        self.screensaver_thread.start()

    def _screensaver_timer(self, timeout=3):
        """
        Screensaver timer that resets the timer when a button is pressed.
        :param timeout: The timeout in seconds.
        """
        while True:
            self._screensaver_time_left = timeout
            while self._screensaver_time_left >= 0:
                print(f"Screen saver timer: {self._screensaver_time_left}s")
                time.sleep(1)
                self._screensaver_time_left -= 1
            print(f"Screen saver starts now.")
            try:
                self._SCREEN_SAVER.view(self.current_view.image)
            except Exception as e:
                print(f"Error in screensaver thread: {e}")
    
    def _reset_screensaver_timer(self):
        """
        Reset the screensaver timer.
        """
        self._screensaver_time_left = self._screensaver_timeout
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
        # get the whole parameter from the function call and store it in context
        #self.current_view_context = {**args, **kwargs}

        # if given a string for the view, get the view object.
        if self.current_view is not None:
            self.current_view.is_active = False

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
                print("Joining thread...")
                self.current_view.break_loop = True  # Break the loop of the current view
                self.view_thread.join(timeout=3) 
            except Exception as e:
                print(f"Error joining thread: {e}")
        self.current_view = view
        self.current_view.is_active = True
        self.view_thread = threading.Thread(target=self.current_view.view, args=args, kwargs=kwargs, daemon=True)
        self.view_thread.start()
        self.signals.view_changed.send(sender=self, view=view)

    def __del__(self):
        self.oled.cleanup()
        print("OLEDViewController cleaned up.")