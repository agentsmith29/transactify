from django.dispatch import Signal
from .OLEDPage import OLEDPage
import os

from .OLEDPageStoreMain import OLEDPageStoreMain

from terminal.api_endpoints.Customer import Customer
from terminal.api_endpoints.StoreProduct import StoreProduct

#from ...webmodels.CustomerBalance import CustomerBalance

class OLEDPagePurchaseSuccessfull(OLEDPage):
    name: str = "OLEDPagePurchaseSuccessfull"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        OLEDPagePurchaseSuccessfull.name: str = str(self.__class__.__name__)

    def view(self, customer: Customer, product: StoreProduct, next_view = None, *args, **kwargs):
        balance = 0#CustomerBalance.objects.get(customer=customer)

        image, draw = self._post_init()

        header_height = 20
        header_text = f"Thank you, {customer.first_name} {customer.last_name}"
        draw.text((20, 0), header_text, font=self.font_large, fill=(255,255,255))  # Leave space for NFC symbol


        self.paste_image(image, r"/app/static/icons/png_16/cart-check-fill.png", (0, 0))
        # Divider line
        draw.line([(0, header_height), (self.width, header_height)], fill=(255,255,255), width=1)
    
        # ------------- Body ----------------
        # Content Section: Display Name, Surname, and Balance
        content_y_start = header_height + 5
        self.paste_image(image, r"/app/static/icons/png_16/cash-stack.png", (0, content_y_start))
        draw.text((30, content_y_start+2), f"Balance: EUR: {customer.balance}", font=self.font_regular, fill=(255,255,255))
        #self.paste_image(image, r"/app/static/icons/png_16/cart4.png", (0, content_y_start+18))
        self.draw_text_warp(0, content_y_start+20, f"Thank you for shopping at {product.store.name}", self.font_regular, fill=(255,255,255))
       
        # Update the OLED display
        self.send_to_display(image)
        # ------------- Body ----------------
        #self.display_next(image, draw, OLEDPageMain.name, 20)
        self.display_next(image, draw, next_view, 5, *args, **kwargs)
    
    def on_barcode_read(self, sender, barcode, **kwargs):
        pass

    def on_nfc_read(self, sender, id, text, **kwargs):
        pass

    def on_btn_pressed(self, sender, kypd_btn, **kwargs):
        if kypd_btn == self.btn_back:
            self.view_controller.request_view(self.view_controller.PAGE_STORE_SELECTION)        
    
