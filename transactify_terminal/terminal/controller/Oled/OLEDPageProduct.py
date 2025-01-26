from django.dispatch import Signal
from .OLEDPage import OLEDPage

import os
import requests

from .OLEDPageStoreMain import OLEDPageStoreMain
from .OLEDStoreSelection import OLEDStoreSelection
from terminal.webmodels.Store import Store
from terminal.api_endpoints.APIFetchStoreProduct import APIFetchStoreProduct

from ...api_endpoints.APIFetchCustomer import Customer
from rest_framework import status

from requests import Response

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from OLEDViewController import OLEDViewController # to avoid circular import, only for type hinting
from ...api_endpoints.APIFetchException import APIFetchException

from decimal import Decimal


class OLEDPageProduct(OLEDPage):
    name: str = "OLEDPageProduct"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        OLEDPageProduct.name: str = str(self.__class__.__name__)
        self.store: Store = None
        self.product: APIFetchStoreProduct = None

    def view(self, product: APIFetchStoreProduct, *args, **kwargs):
        image, draw = super().view()
        self.ledstrip.animate(self.led_animation)
        self.product: APIFetchStoreProduct = product
        self.store: Store = self.product.store
        

        # Header Section
        header_height = 20
        header_text = f"{product.name}"
        draw.text((20, 0), header_text, font=self.font_large, fill=(255,255,255))  # Leave space for NFC symbol
        self.align_right(draw, f"({product.stock_quantity})", 10, self.font_small)

        # Paste the NFC symbol into the header
        self.paste_image(image, f"{self.ICONS}/png_16/cart-dash-fill.png", (0, 0))

        # Divider line
        draw.line([(0, header_height), (self.width, header_height)], fill=(255,255,255), width=1)

        content_y_start = header_height + 5
        fp = Decimal(product.final_price).quantize(Decimal('0.01'))
        if float(product.discount) > 0:
            draw.text((30, content_y_start), f"SALE {fp}", font=self.font_large,fill=(255,255,255))
            #draw.text((30, content_y_start + 25), f"Stock {product.stock_quantity}", font=self.font_regular,fill=(255,255,255))
        else:
            draw.text((30, content_y_start), f"EUR {fp}", font=self.font_large,fill=(255,255,255))
            #draw.text((30, content_y_start + 20), f"Stock {product.stock_quantity}", font=self.font_large,fill=(255,255,255))
        
        if product.stock_quantity == 0:
            draw.text((30, content_y_start + 25), f"Out of stock. Please contact staff.", font=self.font_regular, fill=(255,255,255))
            # --- next view
            self.display_next(image, draw, OLEDStoreSelection.name, 5, store=self.store,)
        else:
            draw.text((30, content_y_start + 25), f"Place NFC to buy from {product.store.name}", font=self.font_regular, fill=(255,255,255))
        # Update the OLED display
        self.send_to_display(image)
        
        
    
    def on_barcode_read(self, sender, barcode, **kwargs):
        self._on_barcode_read_request_products_view(view_controller=self.view_controller, 
                                               stores=self.stores,
                                               barcode=barcode) 

    def on_nfc_read(self, sender, id, **kwargs):
        self._make_purchase(view_controller=self.view_controller, product=self.product, card_number=id)

    def on_btn_pressed(self, sender, kypd_btn, **kwargs):
        if kypd_btn == OLEDPage.BTN_BACK:
            self.ledstrip.stop_animation()
            self.view_controller.request_view(self.view_controller.PAGE_MAIN,
                                              store=self.product.store) 
    

    def _make_purchase(self, view_controller: 'OLEDViewController', product: APIFetchStoreProduct, card_number: str):
        view_controller: OLEDViewController
        # Request the webpage from the current store
        customer = self._fetch_customer(view_controller, product.store, card_number)
        if not customer:
            return
            
        try:
            # Call the make_sale function
            response_make_purchase: Response = product.customer_purchase(customer, quantity=1)
            self.logger.debug(f"Got Response: {status}")
            # make a post to MakePurchase
            if response_make_purchase.status_code == status.HTTP_200_OK:
                # extract message and code
                message = response_make_purchase.json().get("message")
                code = int(response_make_purchase.json().get("code"))
                print("Sold product!")
                customer = self._fetch_customer(view_controller, product.store, card_number)
                if not customer:
                    return  # Should not happen!
                #print(response.status_code, response.content)
                view_controller.request_view(view_controller.PAGE_PURCHASE_SUCC, 
                                        customer=customer, 
                                        product=product,
                                        # Next view handler
                                        next_view=view_controller.PAGE_MAIN,
                                        store=product.store)
        except requests.exceptions.RequestException as e:
            view_controller.request_view(view_controller.PAGE_ERROR, 
                                        error_title=f"Error {e.response.json().get('code')}", 
                                        error_message=e.response.json().get("message"),
                                        # Next view handler
                                        next_view=view_controller.PAGE_MAIN,
                                        store=product.store)
        except Exception as e:
            view_controller.request_view(view_controller.PAGE_ERROR, 
                                        error_title="Error", 
                                        error_message=str(e),
                                        # Next view handler
                                        next_view=view_controller.PAGE_MAIN,
                                        store=product.store)



    def led_animation(self):
        from rpi_ws281x import Color
        try:
            while not self.ledstrip.break_loop:
                self.ledstrip.colorWipe(Color(0, 255, 0), 50)  # Green wipe
                self.ledstrip.colorWipe(Color(0, 0, 0), 50)  # Green wipe
        except KeyboardInterrupt:
            self.ledstrip.colorWipe(Color(0, 0, 0), 10)

        except Exception as e:
            self.ledstrip.colorWipe(Color(0, 0, 0), 10)
