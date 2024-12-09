import os
import logging
import requests

from django.apps import AppConfig
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .HardwareInterface import HardwareInterface
from .Oled.OLEDView import OLEDView

from ..StoreProduct import StoreProduct

from shared.models import Customer

class HardwareController():
    init_counter = 0

    def __init__(self, *args, **kwargs):
        logger = logging.getLogger('store')
        logger.info(f"HardwareController initilized. {HardwareController.init_counter} Number of initializations.")
        HardwareController.init_counter += 1

        lock_interaction = False

        self.hwif = HardwareInterface()
        self.current_view = None #self.view_main
        self.current_products = None #[]
        
        self.hwif.barcode_reader.signals.barcode_read.connect(self.on_barcode_read)
        self.hwif.nfc_reader.signals.tag_read.connect(self.on_nfc_read)
        self.hwif.nfc_reader.signals.tag_reading_status.connect(self.on_nfc_reading_status)

        self.hwif.keypad.signals.key_pressed.connect(self.on_key_pressed)


        self.view = OLEDView(self.hwif.oled)
        self.view.request_view(self.view.PAGE_MAIN)
        
        self.store_bases = []
        for base in os.getenv('TARGET_SERVICES', '').split(','):
            print(f">>>> Adding base: {base}")
            self.store_bases.append(base)

    def on_nfc_reading_status(self, sender, status, **kwargs):
        self.view.current_view.display_nfc_overlay(status)

    def on_key_pressed(self, sender, col, row, btn, **kwargs):
        if self.view.current_view == "view_start_product_management":
            if self.view.button_A_for_release and btn == "A":
                self.view.request_view(self.view.view_main)
        elif self.view.current_view.locked and btn != "A":
            self.view.current_view.display_lock_overlay()
        #elif self.view.current_view.locked and btn == "A":
        #    self.view.request_view(self.view.PAGE_MAIN, unlock=True)
        elif self.view.current_view.overwritable and btn == "A":
            self.view.request_view(self.view.PAGE_MAIN, unlock=True)
        elif self.view.current_view == self.view.PAGE_PRODUCT and btn == "A":
            self.view.request_view(self.view.PAGE_MAIN, unlock=True)
        else:
            print(f"Key pressed: {col}, {row}, {btn}")
    
    def get_target_urls(self):
        """Fetch target URLs from an environment variable."""
        # The environment variable should contain URLs separated by commas
        urls = os.getenv('TARGET_SERVICES', '')  # Example: 'http://service1:8000, http://service2:8000'
        return [url.strip() for url in urls.split(',') if url.strip()]
    
    
    def post_barcode(self, sender, barcode, **kwargs):
        """Handle a barcode read and notify all target services."""
        print(f"Barcode read: {barcode}")
        payload = {"barcode": barcode}
        headers = {"Content-Type": "application/json"}

        if not self.target_urls:
            print("No target URLs configured for notifications.")
            return

        for target_url in self.target_urls:
            try:
                # Send the notification to each target URL
                response = requests.post(f"{target_url}/notify/barcode/", json=payload, headers=headers)
                if response.status_code == 200:
                    print(f"Notification to {target_url} succeeded: {response.json()}")
                else:
                    print(f"Notification to {target_url} failed: {response.status_code}, {response.text}")
            except requests.RequestException as e:
                print(f"Error while sending notification to {target_url}: {e}")

    def on_barcode_read(self, sender, barcode, **kwargs):
        print(f"Barcode read: {barcode}")
        if self.view.current_view == self.view.PAGE_MAIN or self.current_view == self.view.PAGE_PRODUCT:
            self.current_products = StoreProduct.get_product_from_api(self.store_bases, barcode) #StoreProduct.objects.filter(ean=barcode).first()
            print(f"json: {self.current_products}")
            if self.current_products:
                self.view.request_view(self.view.PAGE_PRODUCT, product=self.current_products)
                #self.current_products = product
            else:
                print(f"Product not found: {barcode}")
                self.view.request_view(self.view.PAGE_PRODUCT_UNKNW, ean=barcode)
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
        if self.view.current_view == self.view.PAGE_MAIN:
            customer  = Customer.objects.filter(card_number=id).first()
            if customer:
                self.view.request_view(self.view.PAGE_CUSTOMER, customer=customer)
            else:
                 self.view.request_view(self.view.PAGE_CUSTOMER_UNKNW, id=id)
        elif self.view.current_view == self.view.PAGE_PRODUCT:
            customer = None# Customer.objects.filter(card_number=id).first()
            print(f"Customer: {customer}")
            self.current_nfc = id
            # Iterate through the current products and create a simulated HTTP POST request
            #for p in self.current_products:
            try:# Call the make_sale function
                ret_code, customer, customer_balance, product, purchase_entry = ManageStockHelper.customer_purchase(
                    ean=self.view.PAGE_PRODUCT.product.ean, 
                    quantity=1, 
                    purchase_price=self.view.PAGE_PRODUCT.product.resell_price, 
                    card_number=id)
                # make a post to MakePurchase
                if ret_code == -1:
                    self.view.request_view(self.view.PAGE_CUSTOMER_UNKNW, id=id)
                elif ret_code == -2:
                    print("Insufficient balance")
                    #self.view.request_view(self.view.PAGE_CUSTOMER_BAL, customer=customer)
                elif ret_code == -3:
                    print("Insufficient stock")
                    self.view.request_view(self.view.PAGE_INSUFF_STOCK, 
                                           product=self.view.PAGE_PRODUCT.product)
                elif ret_code == -4:
                    print("Balance mismatch")
                    # self.view.request_view(self.view.PAGE_CUSTOMER_BAL, customer=customer)
                elif ret_code == -5:
                    print("Error during sale. See logs.")
                elif ret_code == 0:
                    print("Sold product!")
                    #print(response.status_code, response.content)
                    self.view.request_view(self.view.PAGE_PURCHASE_SUCC, 
                                           customer=customer, 
                                           product=self.view.PAGE_PRODUCT.product)
                else:
                    print(f"Unknown return code: {ret_code}")
            except Exception as e:
                print(f"Error during sale: {e}")
                #self.view_purchase_failed()

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

class APICalls():

    def custom404(request, exception=None, detail=None):
        return JsonResponse({
            'status_code': 404,
            'error': 'The resource was not found',
            'detail': detail
        })

    def get_customer_list(self):
        # Fetch the list of customers
        customers = []

    def get_customer(base_urls, card_number):
        # product_found = False
        # customer = []
        for base in base_urls:
            base_url = f"http:/{base}/api/"
            # Fetch a single customer
            api_url = f"{base_url}/api/products/{card_number}"
            respond = requests.get(api_url)
            if respond.status_code == 200:
                return respond    


