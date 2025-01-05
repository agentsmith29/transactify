from django.dispatch import Signal
#from  cashlessui.models import Customer

from .OLEDPage import OLEDPage
import os

from .OLEDPageStoreMain import OLEDPageStoreMain

class OLEDPageCustomer_Unknown(OLEDPage):
    name: str = "OLEDPageCustomer_Unknown"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        OLEDPageCustomer_Unknown.name: str = str(self.__class__.__name__)
       
    def view(self, id, next_view=None, *args, **kwargs):
        image, draw = self._post_init()

        header_height = 20
        header_text = f"Unknown Card {id}"
        draw.text((20, 0), header_text, font=self.font_large, fill=(255,255,255))  # Leave space for NFC symbol


       
        self.paste_image(image, r"/app/static/icons/png_16/person-fill-x.png", (0, 0))
        # Divider line
        draw.line([(0, header_height), (self.width, header_height)], fill=(255,255,255), width=1)

        # ------------- Body ----------------
        # Content Section: Display Name, Surname, and Balance
        content_y_start = header_height + 5
        self.paste_image(image, r"/app/static/icons/png_24/person-fill-x.png", (0, content_y_start))
        
        
        self.draw_text_warp(30, content_y_start+2, f"Card is unknown or not bound to a customer.", self.font_regular, fill=(255,255,255))

        # Update the OLED display
        self.send_to_display(image)
        # ------------- Body ----------------
        if next_view:
            self.display_next(image, draw, next_view, 5, *args, **kwargs)
    
    def on_barcode_read(self, sender, barcode, **kwargs):
        pass

    def on_nfc_read(self, sender, id, text, **kwargs):
        pass

    def on_btn_pressed(self, sender, kypd_btn, **kwargs):
        if kypd_btn == OLEDPage.BTN_BACK:
            self.view_controller.request_view(self.view_controller.PAGE_STORE_SELECTION)