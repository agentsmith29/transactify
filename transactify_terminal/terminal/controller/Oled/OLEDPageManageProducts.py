from django.dispatch import Signal
from .OLEDPage import OLEDPage
import os

from .OLEDPageStoreMain import OLEDPageStoreMain

class OLEDPageProducts_Manage(OLEDPage):
    name: str = "OLEDPageProducts_Manage"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        OLEDPageProducts_Manage.name: str = str(self.__class__.__name__)

    def view(self, *args, **kwargs):
        image, draw = super().view()

        # Header Section
        header_height = 20
        header_text = f"Product Management"
        draw.text((20, 0), header_text, font=self.font_large, fill=(255,255,255))  # Leave space for NFC symbol

        # Paste the NFC symbol into the header
        self.paste_image(image, r"/app/static/icons/png_16/gear-fill.png", (0, 0))

        # Divider line
        draw.line([(0, header_height), (self.width, header_height)], fill=(255,255,255), width=1)

       
        content_y_start = header_height + 5
        self.paste_image(image, r"/app/static/icons/png_24/lock.png", (0, content_y_start))
        draw.text((30, content_y_start + 2), f"Terminal is locked and no iteractions are possible", font=self.font_regular,fill=(255,255,255))
        draw.text((30, content_y_start + 14), f"Press A to continue or place NFC to buy", font=self.font_regular, fill=(255,255,255))
        # Update the OLED display
        self.send_to_display(image)

    def on_barcode_read(self, sender, barcode, **kwargs):
        pass

    def on_nfc_read(self, sender, id, **kwargs):
        pass

    def on_btn_pressed(self, sender, kypd_btn, **kwargs):
        if kypd_btn == OLEDPage.BTN_BACK:
            self.view_controller.request_view(self.view_controller.PAGE_STORE_SELECTION)