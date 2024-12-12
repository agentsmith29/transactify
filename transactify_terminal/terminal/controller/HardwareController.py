import os
import logging
import requests

from django.apps import AppConfig
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .HardwareInterface import HardwareInterface
from .Oled.OLEDView import OLEDView
from .ConfParser import parse_services_config_from_yaml
from .ConfParser import Store

from ..api_endpoints.StoreProduct import StoreProduct
from ..api_endpoints.Customer import Customer

from requests.models import Response

class HardwareController():
    init_counter = 0

    def __init__(self, *args, **kwargs):
        logger = logging.getLogger('store')
        logger.info(f"HardwareController initilized. {HardwareController.init_counter} Number of initializations.")
        HardwareController.init_counter += 1

        lock_interaction = False

        self.hwif = HardwareInterface()
        self.current_view = None #self.view_main
        
        
        self.hwif.barcode_reader.signals.barcode_read.connect(self.on_barcode_read)
        self.hwif.nfc_reader.signals.tag_read.connect(self.on_nfc_read)
        self.hwif.nfc_reader.signals.tag_reading_status.connect(self.on_nfc_reading_status)

        self.hwif.keypad.signals.key_pressed.connect(self.on_key_pressed)
        self.view = OLEDView(self.hwif.oled)

       
        self.store_bases = parse_services_config_from_yaml('./terminal.conf')

        # Stores the current selection
        self.selected_store = None
        self.current_products = None

        print(f"Store bases: {self.store_bases}")

        if len(self.store_bases) == 0:
            print("No store bases found. Exiting.")
            exit(1)
        elif len(self.store_bases) == 1:
            self.view.request_view(self.view.PAGE_MAIN, store_name=self.store_bases[0].name, display_back=False, )
        else:
            self.view.request_view(self.view.PAGE_STORE_SELECTION, stores=self.store_bases)
        
        
    def on_nfc_reading_status(self, sender, status, **kwargs):
        self.view.current_view.display_nfc_overlay(status)

    def on_key_pressed(self, sender, col, row, btn, **kwargs):
        if self.view.current_view == self.view.PAGE_STORE_SELECTION:
            # Go to the main view if a store is selected
            for store in self.store_bases:
                if store.terminal_button == btn:
                    self.selected_store = store
                    self.view.request_view(self.view.PAGE_MAIN, store_name=self.selected_store.name, display_back=True)
        elif self.view.current_view == self.view.PAGE_MAIN or self.view.current_view == self.view.PAGE_PRODUCT:
            # Return to store selection, if there are multiple stores
            if btn == "D" and len(self.store_bases) > 1:
                self.view.request_view(self.view.PAGE_STORE_SELECTION, stores=self.store_bases)
        elif self.view.current_view == "view_start_product_management":
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
            try:
                self.current_product = StoreProduct.get_from_api(self.store_bases, barcode)
                self.selected_store = self.current_product.store
                print(f"json: {self.current_products}")
                if self.current_product:
                    self.view.request_view(self.view.PAGE_PRODUCT, product=self.current_product)
                    #self.current_products = product
                else:
                    print(f"Product not found: {barcode}")
                    self.view.request_view(self.view.PAGE_PRODUCT_UNKNW, ean=barcode)
                    #self.view.request_view(self.view.view_unknown_product, barcode)
            except Exception as e:
                print(f"Error fetching product: {e}")
                self.current_product = None
                self.selected_store = None
        elif self.view.current_view == self.view.PAGE_STORE_SELECTION:
            self.current_product = StoreProduct.get_from_api(self.store_bases, barcode)
            self.selected_store = self.current_product.store
            print(f"json: {self.current_products}")
            if self.current_product:
                self.view.request_view(self.view.PAGE_PRODUCT, product=self.current_product)
                #self.current_products = product
            else:
                print(f"Product not found: {barcode}")
                self.view.request_view(self.view.PAGE_PRODUCT_UNKNW, ean=barcode, 
                                       next_view=self.view.PAGE_STORE_SELECTION, stores=self.store_bases)
                #self.view.request_view(self.view.view_unknown_product, barcode)
        else:
            print(f"Barcode read, but no view to handle it: {self.current_view}")
            self.selected_store = None
        


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
            customer  = Customer.get_from_api(self.selected_store, id)
            if customer:
                self.view.request_view(self.view.PAGE_CUSTOMER, customer=customer)
            else:
                 self.view.request_view(self.view.PAGE_CUSTOMER_UNKNW, id=id)
        elif self.view.current_view == self.view.PAGE_PRODUCT:
            # Request the webpage from the current store
            customer = Customer.get_from_api(self.current_product.store, id)
            print(f"Customer: {customer}")
            self.current_nfc = id
            # Iterate through the current products and create a simulated HTTP POST request
            #for p in self.current_products:
            try:# Call the make_sale function
                status: Response = self.current_product.customer_purchase(customer, quantity=1)
                print(f"Got Response: {status}")
                # make a post to MakePurchase
                if status.status_code == 210:
                    # extract message and code
                    message = status.json().get("message")
                    code = int(status.json().get("code"))
                    print("Sold product!")
                    #print(response.status_code, response.content)
                    self.view.request_view(self.view.PAGE_PURCHASE_SUCC, 
                                           customer=customer, 
                                           product=self.current_product,
                                           next_view=self.view.PAGE_MAIN,
                                           store_name=self.selected_store.name,
                                           display_back=True)
                else:
                    error = status.json().get("error")
                    code = int(status.json().get("code"))
                    if code == 10:
                        self.view.request_view(self.view.PAGE_CUSTOMER_UNKNW, id=id)
                    elif code == 200:
                        print("Insufficient stock")
                        self.view.request_view(self.view.PAGE_INSUFF_STOCK, 
                                            product=self.view.PAGE_PRODUCT.product)
                    else:
                        print(f"Unknown return code: {status.status_code}")
                        self.view.request_view(self.view.PAGE_ERROR, 
                                               error_title="error", error_message=error,
                                            next_view=self.view.PAGE_MAIN,
                                            store_name=self.selected_store.name,
                                            display_back=True)
                    
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


