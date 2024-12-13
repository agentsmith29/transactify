from django.dispatch import Signal
#from cashlessui.models import Customer
#from ...webmodels.CustomerBalance import CustomerBalance

from .OLEDPage import OLEDPage
import os

from .OLEDPageStoreMain import OLEDPageStoreMain

class OLEDPageCustomer(OLEDPage):
    name: str = "OLEDPageCustomer"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        OLEDPageCustomer.name: str = str(self.__class__.__name__)

    def view(self, customer, *args, **kwargs):
        #balance = CustomerBalance.objects.get(customer=customer)
        image, draw = self._post_init()

        header_height = 20
        header_text = f"Hello, {customer.user.first_name} {customer.user.last_name}"
        draw.text((20, 0), header_text, font=self.font_large, fill=(255,255,255))  # Leave space for NFC symbol


        self.paste_image(image, r"/app/static/icons/png_16/person-bounding-box.png", (0, 0))
        # Divider line
        draw.line([(0, header_height), (self.width, header_height)], fill=(255,255,255), width=1)

        # ------------- Body ----------------
        # Content Section: Display Name, Surname, and Balance
        content_y_start = header_height + 5
        self.paste_image(image, r"/app/static/icons/png_16/cash-stack.png", (0, content_y_start))
        draw.text((30, content_y_start+2), f"Balance: EUR: {customer.get_balance(None)}", font=self.font_regular, fill=(255,255,255))
        self.paste_image(image, r"/app/static/icons/png_16/cart4.png", (0, content_y_start+18))
        draw.text((30, content_y_start+20), f"Last purchase:", font=self.font_regular, fill=(255,255,255))

        # Update the OLED display
        self.oled.display(image)
        # ------------- Body ----------------
        self.display_next(image, draw, OLEDPageStoreMain.name, 20)
    
    def on_barcode_read(self, sender, barcode, **kwargs):
        pass

    def on_nfc_read(self, sender, id, text, **kwargs):
        pass

    def on_btn_pressed(self, sender, kypd_btn, **kwargs):
        if kypd_btn == self.btn_back:
            self.view_controller.request_view(self.view_controller.PAGE_STORE_SELECTION)

    
