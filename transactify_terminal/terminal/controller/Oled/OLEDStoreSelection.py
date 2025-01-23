from django.dispatch import Signal

from terminal.webmodels.Store import Store
from .OLEDPage import OLEDPage
import os

from terminal.api_endpoints.APIFetchStoreProduct import APIFetchStoreProduct
from terminal.api_endpoints.APIFetchCustomer import Customer
import requests

class OLEDStoreSelection(OLEDPage):
    name: str = "OLEDStoreSelection"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        OLEDStoreSelection.name: str = str(self.__class__.__name__) 

    def view(self, *args, **kwargs):
        if len(self.stores) == 1:
            self.selected_store = self.stores[0]
            self.logger.debug(f"Only one store found, selecting store: {self.selected_store}")
            self.view_controller.request_view(self.view_controller.PAGE_MAIN, store=self.selected_store, display_back=False)
            return
        image, draw = super().view()

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

        
        if len(self.stores) == 0:
            draw.text((30, content_y_start), f"No stores found", font=self.font_small, fill=(255,255,255))
        else:
            draw.text((30, content_y_start), f"Select the Store", font=self.font_small, fill=(255,255,255))
            for i, store in enumerate(self.stores):
                draw.text((30, content_y_start + 10 + i*10), f"{store.terminal_button}: {store.name}", font=self.font_small, fill=(255,255,255))

        # Update the OLED display
        self.send_to_display(image)
        # ------------- Body ----------------

    def on_btn_pressed(self, sender, kypd_btn, **kwargs):
        for store in self.stores:
            if store.terminal_button == kypd_btn:
                self.selected_store = store
                self.view_controller.request_view(self.view_controller.PAGE_MAIN,
                                                  store=self.selected_store, display_back=True)
        #self.display_message_overlay("Scan NFC to select store")
    

    def on_nfc_read(self, sender, id, **kwargs):
        #customer_entries = [self._fetch_customer(self.view_controller, store, card_number=id) for store in self.stores if not None]
        customer_entries = []
        if len(self.stores) == 0:
            self.logger.warning("No stores found, cannot fetch customer.")
            return
        
        for store in self.stores:
            customer = self._fetch_customer(self.view_controller, store, card_number=id)
            if customer is not None:
                customer_entries.append(customer)

        self.logger.debug(f"Found customer entries: {customer_entries}")
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
        self.logger.debug(f"OLED page received barcode: {barcode}")
        self._on_barcode_read_request_products_view(view_controller=self.view_controller, 
                                               stores=self.stores,
                                               barcode=barcode) 
        
    def on_websocket_connect(self, sender, **kwargs):
        self.view()
    
    def on_websocket_disconnect(self, sender, **kwargs):
        self.view()
    

         