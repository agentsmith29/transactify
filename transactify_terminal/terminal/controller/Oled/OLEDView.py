from .OLEDStoreSelection import OLEDStoreSelection
from .OLEDPage import OLEDPage
from .OLEDMainPage import OLEDPageMain
from .OLEDPageProduct import OLEDPageProduct
from .OLEDPageManageProducts import OLEDPageProducts_Manage
from .OLEDPageUnknownProduct import OLEDPageProduct_Unknown

from .OLEDPageCustomer import OLEDPageCustomer
from .OLEDPageCustomerUnknown import OLEDPageCustomer_Unknown
from .OLEDPagePurchaseSuccessfull import OLEDPagePurchaseSuccessfull

from .OLEDPageInsufficientStock import OLEDPageInsufficientStock

from .OLEDPageError import OLEDPageError


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

        self.PAGE_STORE_SELECTION = OLEDStoreSelection(oled, self.sig_abort_page, self.sig_request_view)

        self.PAGE_MAIN = OLEDPageMain(oled, self.sig_abort_page, self.sig_request_view)

        self.PAGE_INSUFF_STOCK = OLEDPageInsufficientStock(oled, self.sig_abort_page, self.sig_request_view)
        
        self.PAGE_PRODUCT = OLEDPageProduct(oled, self.sig_abort_page, self.sig_request_view)
        self.PAGE_PRODUCT_UNKNW = OLEDPageProduct_Unknown(oled, self.sig_abort_page, self.sig_request_view)
        self.PAGE_PRODUCTS_MGM = OLEDPageProducts_Manage(oled, self.sig_abort_page, self.sig_request_view)
        
        
        self.PAGE_CUSTOMER = OLEDPageCustomer(oled, self.sig_abort_page, self.sig_request_view)
        self.PAGE_CUSTOMER_UNKNW = OLEDPageCustomer_Unknown(oled, self.sig_abort_page, self.sig_request_view)

        self.PAGE_PURCHASE_SUCC = OLEDPagePurchaseSuccessfull(oled, self.sig_abort_page, self.sig_request_view)

        self.PAGE_ERROR = OLEDPageError(oled, self.sig_abort_page, self.sig_request_view)

        self.oled = oled
        
        # Stores the current view. Needed, to allow the controller to respond differently to events
        self.current_view: OLEDPage = None 
    

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

        