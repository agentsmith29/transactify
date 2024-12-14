from django.dispatch import Signal
from .OLEDPage import OLEDPage
import os

from .OLEDPageStoreMain import OLEDPageStoreMain

class OLEDPageProduct_Unknown(OLEDPage):
    name: str = "OLEDPageProduct_Unknown"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        OLEDPageProduct_Unknown.name: str = str(self.__class__.__name__)

    def view(self, ean, next_view = None, *args, **kwargs):
        image, draw = self._post_init()

        # Header Section
        header_height = 20
        header_text = f"Unknown Product."
        draw.text((20, 0), header_text, font=self.font_large, fill=(255,255,255))  # Leave space for NFC symbol

        # Paste the NFC symbol into the header
        self.paste_image(image, r"/app/static/icons/png_16/cart-dash-fill.png", (0, 0))

        # Divider line
        draw.line([(0, header_height), (self.width, header_height)], fill=(255,255,255), width=1)

        content_y_start = header_height + 5
        ip_address = f"{os.getenv('DJANGO_WEB_HOST')}:{os.getenv('DJANGO_WEB_PORT')}"

        self.draw_text_warp(10,  content_y_start+2, 
                             f"The scanned poduct ({ean}) was not found in the database. Please add it using the web-interface under {ip_address}",
                             self.font_small, fill=(255,255,255))

        # Update the OLED display
        self.oled.display(image)
        if next_view:
            self.display_next(image, draw, next_view, 5, *args, **kwargs)
       

