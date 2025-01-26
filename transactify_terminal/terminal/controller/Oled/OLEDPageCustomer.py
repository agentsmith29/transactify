from django.dispatch import Signal
#from cashlessui.models import Customer
#from ...webmodels.CustomerBalance import CustomerBalance

from .OLEDPage import OLEDPage
import os

from .OLEDPageStoreMain import OLEDPageStoreMain

from terminal.api_endpoints.APIFetchCustomer import Customer
from terminal.webmodels.Store import Store


class OLEDPageCustomer(OLEDPage):
    name: str = "OLEDPageCustomer"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        OLEDPageCustomer.name: str = str(self.__class__.__name__)
        self.store = None
        self.customer = None

    def view(self, store: Store, customer: Customer, next_view, *args, **kwargs):
        image, draw = super().view()
        self.store: Store = store
        self.customer: Customer = customer

        header_height = 20
        header_text = f"Hello, {customer.first_name} {customer.last_name}"
        draw.text((20, 0), header_text, font=self.font_large, fill=(255,255,255))  # Leave space for NFC symbol


        self.paste_image(image, f"${APP_DIR}/../static/icons/png_16/person-bounding-box.png", (0, 0))
        # Divider line
        draw.line([(0, header_height), (self.width, header_height)], fill=(255,255,255), width=1)

        # ------------- Body ----------------
        # Content Section: Display Name, Surname, and Balance
        content_y_start = header_height + 3
        self.paste_image(image, f"{self.ICONS}/png_12/cart3.png", (0, content_y_start+1))
        draw.text((30, content_y_start+2), f"Selected store: {store.name}", font=self.font_regular, fill=(255,255,255))

        self.paste_image(image, f"{self.ICONS}/png_12/cash-stack.png", (0, content_y_start+15))
        draw.text((30, content_y_start+14), f"Balance: EUR: {customer.balance}", font=self.font_regular, fill=(255,255,255))
        
        self.paste_image(image, f"{self.ICONS}/png_12/cart4.png", (0, content_y_start+27))
        draw.text((30, content_y_start+28), f"Last purchase: {customer.last_changed}", font=self.font_regular, fill=(255,255,255))

        # Update the OLED display
        self.send_to_display(image)
        # ------------- Body ----------------
        if next_view:
            self.display_next(image, draw, next_view, 5, *args, **kwargs)
    
    def on_barcode_read(self, sender, barcode, **kwargs):
        pass

    def on_nfc_read(self, sender, id, **kwargs):
        pass

    def on_btn_pressed(self, sender, kypd_btn, **kwargs):
        if kypd_btn == OLEDPage.BTN_BACK:
            self.break_loop = True
            self.view_controller.request_view(self.view_controller.PAGE_STORE_SELECTION)

    
