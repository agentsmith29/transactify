from django.dispatch import Signal

from .OLEDPage import OLEDPage
import os

from ..ConfParser import Store


class OLEDPageStoreMain(OLEDPage):
    name: str = "OLEDPageStoreMain"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        OLEDPageStoreMain.name: str = str(self.__class__.__name__)
        self.store: Store = None

    
    def view(self, store: Store, *args, **kwargs):
        self.store: Store = store

        image, draw = self._post_init()

        # Header Section
        header_height = 20
        draw.text((20, 0),  self.store.name, font=self.font_large, fill=(255,255,255))  # Leave space for NFC symbol

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

        #if display_back:
        #    draw.text((30, content_y_start + 10), f"Press 'D' to go back", font=self.font_small, fill=(255,255,255))
        # Update the OLED display
        self.send_to_display(image)
        # ------------- Body ----------------

    def on_barcode_read(self, sender, barcode, **kwargs):
        self._on_barcode_read_request_products_view(view_controller=self.view_controller, 
                                               stores=self.stores,
                                               barcode=barcode) 

    def on_nfc_read(self, sender, id, text, **kwargs):
        customer_entry = self._fetch_customer(view_controller=self.view_controller, 
                                                store=self.store, 
                                                card_number=id)
        self.view_controller.request_view(self.view_controller.PAGE_CUSTOMER, 
                                              store=self.store, 
                                              customer=customer_entry,
                                              # Next view handler
                                              next_view=self.view_controller.PAGE_STORE_SELECTION)

    def on_btn_pressed(self, sender, kypd_btn, **kwargs):
        if kypd_btn == OLEDPage.BTN_BACK:
            self.view_controller.request_view(self.view_controller.PAGE_STORE_SELECTION)
