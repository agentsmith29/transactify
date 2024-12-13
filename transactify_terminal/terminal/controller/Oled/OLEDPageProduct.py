from django.dispatch import Signal
from .OLEDPage import OLEDPage
#from ...StoreProduct import StoreProduct

import os
import requests

from .OLEDPageStoreMain import OLEDPageStoreMain
from ...api_endpoints.StoreProduct import StoreProduct
from ..ConfParser import Store

class OLEDPageProduct(OLEDPage):
    name: str = "OLEDPageProduct"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        OLEDPageProduct.name: str = str(self.__class__.__name__)
        self.store: Store = None
        self.product: StoreProduct = None

    def view(self, product: StoreProduct, *args, **kwargs):
        self.product: StoreProduct = product
        self.store: Store = self.product.store
        

        image, draw = self._post_init()

        # Header Section
        header_height = 20
        header_text = f"{product.name}"
        draw.text((20, 0), header_text, font=self.font_large, fill=(255,255,255))  # Leave space for NFC symbol
        self.align_right(draw, f"({product.stock_quantity})", 10, self.font_small)

        # Paste the NFC symbol into the header
        self.paste_image(image, r"/app/static/icons/png_16/cart-dash-fill.png", (0, 0))

        # Divider line
        draw.line([(0, header_height), (self.width, header_height)], fill=(255,255,255), width=1)

        content_y_start = header_height + 5
        if float(product.discount) > 0:
            draw.text((30, content_y_start), f"SALE {product.final_price}", font=self.font_large,fill=(255,255,255))
            #draw.text((30, content_y_start + 25), f"Stock {product.stock_quantity}", font=self.font_regular,fill=(255,255,255))
        else:
            draw.text((30, content_y_start), f"EUR {product.final_price}", font=self.font_large,fill=(255,255,255))
            #draw.text((30, content_y_start + 20), f"Stock {product.stock_quantity}", font=self.font_large,fill=(255,255,255))
        
        draw.text((30, content_y_start + 25), f"Place NFC to buy from {product.store.name}", font=self.font_regular, fill=(255,255,255))
        # Update the OLED display
        self.oled.display(image)
        #self.display_next(image, draw, OLEDPageMain.name, 5)
        
    
    def on_barcode_read(self, sender, barcode, **kwargs):
        self._on_barcode_read_request_products_view(view_controller=self.view_controller, 
                                               stores=self.stores,
                                               barcode=barcode) 

    def on_nfc_read(self, sender, id, text, **kwargs):
        pass

    def on_btn_pressed(self, sender, kypd_btn, **kwargs):
        if kypd_btn == self.btn_back:
            self.view_controller.request_view(self.view_controller.PAGE_MAIN,
                                              store=self.product.store) 
            