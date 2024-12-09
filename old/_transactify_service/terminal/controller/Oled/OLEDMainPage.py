from django.dispatch import Signal

from .OLEDPage import OLEDPage
import os


class OLEDPageMain(OLEDPage):
    name: str = "OLEDPageMain"

    def __init__(self, oled, sig_abort_view: Signal, sig_request_view: Signal, *args, **kwargs):
        super().__init__(oled, 
                         sig_abort_view=sig_abort_view, sig_request_view=sig_request_view,
                         *args, **kwargs)
        OLEDPageMain.name: str = str(self.__class__.__name__)

    def view(self, *args, **kwargs):
        image, draw = self._post_init()

        # Header Section
        header_height = 20
        header_text = f"Don Knabberello"
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
        draw.text((30, content_y_start), f"Scan a product of your choice", font=self.font_small, fill=(255,255,255))
       
        # Update the OLED display
        self.oled.display(image)
        # ------------- Body ----------------

