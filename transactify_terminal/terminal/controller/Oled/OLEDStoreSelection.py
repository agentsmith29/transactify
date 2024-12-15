from django.dispatch import Signal

from ..ConfParser import Store

from .OLEDPage import OLEDPage
import os

from ...api_endpoints.StoreProduct import StoreProduct
from ...api_endpoints.Customer import Customer
import requests

class OLEDStoreSelection(OLEDPage):
    name: str = "OLEDStoreSelection"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        OLEDStoreSelection.name: str = str(self.__class__.__name__) 

    def view(self, *args, **kwargs):
        image, draw = self._post_init()

        # Header Section
        header_height = 20
        header_text = f"Transactify Terminal"
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
        draw.text((30, content_y_start), f"Select the Store", font=self.font_small, fill=(255,255,255))
        for i, store in enumerate(self.stores):
            draw.text((30, content_y_start + 10 + i*10), f"{store.terminal_button}: {store.name}", font=self.font_small, fill=(255,255,255))
       
        # Update the OLED display
        self.oled.display(image)
        # ------------- Body ----------------

    def on_btn_pressed(self, sender, kypd_btn, **kwargs):
        print(f"Button {kypd_btn} pressed")
        for store in self.stores:
            if store.terminal_button == kypd_btn:
                self.selected_store = store
                self.view_controller.request_view(self.view_controller.PAGE_MAIN,
                                                  store=self.selected_store, display_back=True)
        self.display_message_overlay("Scan NFC to select store")
    
    def _fetch_customer(self, view_controller: 'OLEDViewController', store: StoreProduct, card_number: str):
        try:
            return Customer.get_from_api(store, card_number)
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            if int(e.response.json().get('code')) != 10:
                view_controller.request_view(view_controller.PAGE_ERROR, 
                                        error_title=f"Error {e.response.json().get('code')}", 
                                        error_message=e.response.json().get("message"),
                                        # Next view handler
                                        next_view=view_controller.PAGE_MAIN,
                                        store=store)
            return None
        
    def on_nfc_read(self, sender, id, text, **kwargs):
        #customer_entries = [self._fetch_customer(self.view_controller, store, card_number=id) for store in self.stores if not None]
        customer_entries = []
        for store in self.stores:
            customer = self._fetch_customer(self.view_controller, store, card_number=id)
            if customer is not None:
                customer_entries.append(customer)

        print(f"Customer entries: {customer_entries}")
        if len(customer_entries) == 0:
            self.view_controller.request_view(self.view_controller.PAGE_CUSTOMER_UNKNW,
                                             id=id,
                                             # Next view handler
                                            next_view=self.view_controller.PAGE_STORE_SELECTION)
        elif len(customer_entries) == 1:
            self.view_controller.request_view(self.view_controller.PAGE_CUSTOMER, 
                                              store=customer_entries[0].store, 
                                              customer=customer_entries[0],
                                              # Next view handler
                                              next_view=self.view_controller.PAGE_STORE_SELECTION)
        
        elif len(customer_entries) > 1:
            self.display_message_overlay("Multiple store entries. Please use select the store to display the balance.")


    def on_barcode_read(self, sender, barcode, **kwargs):
        self._on_barcode_read_request_products_view(view_controller=self.view_controller, 
                                               stores=self.stores,
                                               barcode=barcode) 
    

         