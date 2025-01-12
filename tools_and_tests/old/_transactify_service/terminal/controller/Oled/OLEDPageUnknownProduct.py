from django.dispatch import Signal
from .OLEDPage import OLEDPage
import os

from .OLEDMainPage import OLEDPageMain

class OLEDPageProduct_Unknown(OLEDPage):
    name: str = "OLEDPageProduct_Unknown"

    def __init__(self, oled, sig_abort_view: Signal, sig_request_view: Signal, *args, **kwargs):
        super().__init__(oled,
                         sig_abort_view=sig_abort_view, sig_request_view=sig_request_view,
                         *args, **kwargs)

    def view(self, ean, *args, **kwargs):
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
        draw.text((10, content_y_start),      f"The scanned poduct ({ean}) was not found ", font=self.font_small,fill=(255,255,255))
        draw.text((10, content_y_start + 14), f"in the database. Please add it using the web-", font=self.font_small,fill=(255,255,255))
        draw.text((10, content_y_start + 28), f"interface under {ip_address}", font=self.font_small,fill=(255,255,255))
       
        # Update the OLED display
        self.oled.display(image)
        
        self.display_next(image, draw, OLEDPageMain, 5)
       

