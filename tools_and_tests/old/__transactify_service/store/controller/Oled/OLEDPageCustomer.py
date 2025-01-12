from django.dispatch import Signal
from cashlessui.models import Customer
from ...webmodels.CustomerBalance import CustomerBalance

from .OLEDPage import OLEDPage
import os

from .OLEDMainPage import OLEDPageMain

class OLEDPageCustomer(OLEDPage):
    name: str = "OLEDPageCustomer"

    def __init__(self, oled, sig_abort_view: Signal, sig_request_view: Signal, *args, **kwargs):
        super().__init__(oled,sig_abort_view=sig_abort_view, sig_request_view=sig_request_view,
                         *args, **kwargs)

    def view(self, customer: Customer, *args, **kwargs):
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
        draw.text((30, content_y_start+2), f"Balance: EUR: {customer.get_balance(CustomerBalance)}", font=self.font_regular, fill=(255,255,255))
        self.paste_image(image, r"/app/static/icons/png_16/cart4.png", (0, content_y_start+18))
        draw.text((30, content_y_start+20), f"Last purchase:", font=self.font_regular, fill=(255,255,255))

        # Update the OLED display
        self.oled.display(image)
        # ------------- Body ----------------
        self.display_next(image, draw, OLEDPageMain.name, 20)
        
    
