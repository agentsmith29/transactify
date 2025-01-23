from django.dispatch import Signal
#from cashlessui.models import Customer
#from ...webmodels.CustomerBalance import CustomerBalance

from .OLEDPage import OLEDPage
import os

from .OLEDPageStoreMain import OLEDPageStoreMain

from terminal.api_endpoints.APIFetchCustomer import Customer
from terminal.webmodels.Store import Store


class OLEDPageManagementLocked(OLEDPage):
    name: str = "OLEDPageManagementLocked"

    def __init__(self, sig_on_page_disconnect, *args, **kwargs):
        super().__init__(*args, **kwargs, locked=True)
        OLEDPageManagementLocked.name: str = str(self.__class__.__name__)

        self.page = None
        self.next_view = None
        self.args = None
        self.kwargs = None

        self.sig_on_page_disconnect = sig_on_page_disconnect
        self.sig_on_page_disconnect.connect(self.on_page_disconnect)

    def view(self, header, icon, text, page, next_view: OLEDPage, *args, **kwargs):

        self.page = page
        self.next_view = next_view
        self.args = args
        self.kwargs = kwargs

        image, draw = super().view()
        header_height = self.display_header(header, icon, 20)

        # ------------- Body ----------------
        # Content Section: Display Name, Surname, and Balance
        content_y_start = header_height + 3
        self.paste_image(image, r"/app/static/icons/png_12/cart3.png", (0, content_y_start+1))
        lines = self.wrap_text(text, self.font_regular, 30, 255)
        for line, y in lines:
            draw.text((20, content_y_start + y), line, font=self.font_small, fill=(255,255,255))


        # Update the OLED display
        self.send_to_display(image)
        # ------------- Body ----------------

    
    def on_barcode_read(self, sender, barcode, **kwargs):
        pass

    def on_nfc_read(self, sender, id, **kwargs):
        pass

    def on_btn_pressed(self, sender, kypd_btn, **kwargs):
        if kypd_btn == OLEDPage.BTN_BACK:
            self.break_loop = True
            self.view_controller.request_view(self.view_controller.PAGE_STORE_SELECTION)

    def on_page_disconnect(self, sender, page, **kwargs):
        if page == self.page:
            self.locked = False
            self.break_loop = True
            self.view_controller.request_view(self.next_view, *self.args, **self.kwargs)

