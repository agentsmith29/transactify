from django.dispatch import Signal

from .OLEDPage import OLEDPage
import os


class OLEDPageError(OLEDPage):
    name: str = "OLEDPageGenericError"

    def __init__(self, oled, sig_abort_view: Signal, sig_request_view: Signal, *args, **kwargs):
        super().__init__(oled, 
                         sig_abort_view=sig_abort_view, sig_request_view=sig_request_view,
                         *args, **kwargs)
        OLEDPageError.name: str = str(self.__class__.__name__)

    
    def view(self, error_title, error_message,
             icon=r'/app/static/icons/png_16/x-circle-fill', 
             display_back = False,
             next_view = None, *args, **kwargs):
        image, draw = self._post_init()

        header_height = 20
        draw.text((20, 0), error_title, font=self.font_large, fill=(255,255,255))  # Leave space for NFC symbol

        self.paste_image(image,icon, (0, 0))
        # Divider line
        draw.line([(0, header_height), (self.width, header_height)], fill=(255,255,255), width=1)

        # ------------- Body ----------------
        # Content Section: Display Name, Surname, and Balance
        content_y_start = header_height + 5
        self.paste_image(image, icon, (0, content_y_start))
        # Wrap the text and draw it
        lines = self.wrap_text(draw, error_message, self.font_regular, offset=10, width=256)

        for line, y in lines:
            draw.text((10, y), line, font=self.font_regular, fill="black")

        # Update the OLED display
        self.oled.display(image)
        # ------------- Body ----------------
        #self.display_next(image, draw, OLEDPageMain.name, 10)

