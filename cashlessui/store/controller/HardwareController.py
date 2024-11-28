from django.apps import AppConfig
from .HardwareInterface import HardwareInterface


from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from concurrent.futures import ThreadPoolExecutor

from ..webmodels.StoreProduct import StoreProduct
from cashlessui.models import Customer

from django.http import HttpRequest

from .Oled.OLEDView import OLEDView

class HardwareController():
    init_counter = 0

    def __init__(self, *args, **kwargs):
        print(f"HardwareController: __init__: {HardwareController.init_counter}")
        HardwareController.init_counter += 1

        lock_interaction = False

        self.hwif = HardwareInterface()
        self.current_view = None #self.view_main
        self.current_products = []
        
        self.hwif.barcode_reader.signals.barcode_read.connect(self.on_barcode_read)
        self.hwif.nfc_reader.signals.tag_read.connect(self.on_nfc_read)
        self.hwif.keypad.signals.key_pressed.connect(self.on_key_pressed)


        self.view = OLEDView(self.hwif.oled)
        self.view.request_view(self.view.PAGE_MAIN)


    def lock_hardware(self):
        lock_interaction = True

    def on_key_pressed(self, sender, col, row, btn, **kwargs):
        if self.view.current_view == "view_start_product_management":
            if self.view.button_A_for_release and btn == "A":
                self.view.request_view(self.view.view_main)
        elif self.view.current_view.locked and btn != "A":
            self.view.current_view.display_lock_overlay()
        elif self.view.current_view.locked and btn == "A":
            self.view.request_view(self.view.PAGE_MAIN, unlock=True)
        else:
            print(f"Key pressed: {col}, {row}, {btn}")

    def on_barcode_read(self, sender, barcode, **kwargs):
        print(f"Barcode read: {barcode}")
        if self.view.current_view == self.view.PAGE_MAIN or self.current_view == self.view.PAGE_PRICE:
            product = StoreProduct.objects.filter(ean=barcode).first()
            if product:
                self.view.request_view(self.view.PAGE_PRICE, product_name=product.name, price=product.resell_price)
                # self.current_products.append(product)
            else:
                print(f"Product not found: {barcode}")
                self.view.request_view(self.view.PAGE_UNKNOWN_PRODUCT, ean=barcode)
                #self.view.request_view(self.view.view_unknown_product, barcode)
        else:
            print(f"Barcode read, but no view to handle it: {self.current_view}")
        self.send_message_to_page(
            "page_manage_products",
            {
                "type": "page_message",
                "message": f"New scanned barcode: {barcode}",
                "barcode": barcode,
            }
        )
        # self.view_price(barcode)
        # self.view_main()
        
    def on_nfc_read(self, sender, id, text, **kwargs):
        print(f"NFC read {id}: {text}")
        if self.view.current_view == "view_main":
            print(Customer.objects.all())
            customer = Customer.objects.get(card_number=id)
            if customer:
                self.view.request_view(self.view.customer_info, customer)
            else:
                 self.view.request_view(self.view.unknown_card)
        elif self.current_view == "view_price":
            customer = Customer.objects.filter(card_number=id).first()
            print(f"Customer: {customer}")
            self.current_nfc = id
            if customer is self.current_nfc:
                print("Customer is the same")
                self.view_purchase_succesfull()
                return

            from ..views import make_sale

            # Iterate through the current products and create a simulated HTTP POST request
            for p in self.current_products:
                request = HttpRequest()
                request.method = 'POST'
                request.POST = {
                    'ean': p.ean,
                    'quantity': 1,
                    'sale_price': str(p.resell_price),  # Ensure the price is a string for POST
                    'customer': customer # Use customer ID
                }

                # Call the make_sale function
                response = make_sale(request)
                print("Sold product!")

                # Optionally handle the response if needed
                print(response.status_code, response.content)
                self.view_purchase_succesfull()

        elif self.current_view == "view_start_card_management":
            self.send_message_to_page(
                "page_view_customers",
                {
                    "type": "page_message",
                    "message": f"New scanned card: {id}",
                    "card_id": id,
                    "text": text,

                }
            )
    
    def nfc_write(self, text):
        """Simulates an NFC write."""
        #loop = asyncio.get_event_loop()
        #await loop.run_in_executor(None, self.reader.write, text)
        self.hwif.nfc_reader.write(text)

    def send_message_to_page(self, page, payload):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            page, 
            payload,
        )
    



    