import os
import logging
import requests

from django.apps import AppConfig
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.dispatch import Signal
def check_run_server():
    _rs = os.getenv('RUN_SERVER', "False").lower()
    if _rs == "true" or _rs == "1":
        return True
    return False
    
RUN_SERVER = check_run_server()
if RUN_SERVER:
    from .HardwareInterface import HardwareInterface
    from .Oled.OLEDViewController import OLEDViewController

from terminal.webmodels.Store import Store

from terminal.webmodels.Store import Store

from terminal.api_endpoints.APIFetchStoreProduct import APIFetchStoreProduct
from ..api_endpoints.APIFetchCustomer import Customer

from requests.models import Response
import threading
import os
from terminal.consumers.TerminalConsumer import WebsocketSignals

from transactify_terminal.settings import CONFIG

class HardwareController():
    init_counter = 0

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(f"{CONFIG.webservice.SERVICE_NAME}.{self.__class__.__name__}")     
        if not RUN_SERVER:
            self.logger.info(f"RUN_SERVER={RUN_SERVER}: Not running server. Exiting HardwareController init.")
            return
        else:
            self.logger.warning(f"RUN_SERVER={RUN_SERVER}: Continuing HardwareController init.")
     
        self.logger.info(f"HardwareController initilized. {HardwareController.init_counter} number of initializations.")
        HardwareController.init_counter += 1
        if HardwareController.init_counter > 1:
            self.logger.error("Multiple initializations of HardwareController. Skipping this initialization.")
            return

        lock_interaction = False

        self.hwif = HardwareInterface()
        self.hwif.signals.nfc_thread_status.connect(self.on_nfc_thread_status_changed)
        self.hwif.signals.barcode_thread_status.connect(self.on_barcode_thread_status_changed)
        self.hwif.signals.keypad_thread_status.connect(self.on_keypad_thread_status_changed)

        self.current_view = None #self.view_main
        
        
        self.hwif.barcode_reader.signals.barcode_read.connect(self.on_barcode_read)
        #self.hwif.nfc_reader.signals.tag_read.connect(self.on_nfc_read)
        self.hwif.nfc_reader.signals.tag_reading_status.connect(self.on_nfc_reading_status)
        self.hwif.nfc_reader.signals.nfc_tag_id_read.connect(self.on_nfc_tag_id_read)

        #self.hwif.keypad.signals.key_pressed.connect(self.on_key_pressed)
        #self.store_bases = list(Store.objects.filter(is_connected=True).order_by('terminal_button'))

        WebsocketSignals.on_connect.connect(self.on_websocket_connect)
        WebsocketSignals.on_disconnect.connect(self.on_websocket_disconnect)

        self.view_controller = OLEDViewController(self.hwif.oled,
                                                  self.hwif.barcode_reader.signals.barcode_read,
                                                  self.hwif.nfc_reader.signals.nfc_tag_id_read,
                                                  self.hwif.keypad.signals.key_pressed,
                                                  #
                                                  WebsocketSignals.on_connect,
                                                  WebsocketSignals.on_disconnect,
                                                  #
                                                  ledstrip=self.hwif.ledstrip)
        
        self.view_controller.signals.view_changed.connect(self.on_view_changed)

       


        # Stores the current selection
        self.selected_store = None
        self.current_products = None

        #print(f"Store bases: {self.store_bases}")

        #if len(self.store_bases) == 1:
        #    self.view_controller.request_view(self.view_controller.PAGE_MAIN, 
        #                                      store=self.store_bases[0], display_back=False)
        #else:
        self.logger.info("HardwareController initialized. Requesting store selection view.")
        self.view_controller.request_view(self.view_controller.PAGE_STORE_SELECTION)


    def on_nfc_reading_status(self, sender, status, **kwargs):
        self.view_controller.current_view.display_nfc_overlay(status)
    
    # =================================================================================================================
    # Event handlers
    # =================================================================================================================
    
    # Thread status handlers
    def on_nfc_thread_status_changed(self, sender, is_alive, **kwargs):
        if not is_alive:
            self.logger.info("NFC thread seems to be dead. Restarting...")
            self.hwif.nfc_reader.start()
    
    def on_barcode_thread_status_changed(self, sender, is_alive, **kwargs):
        if not is_alive:
            self.logger.info("Barcode thread seems to be dead.")

    def on_keypad_thread_status_changed(self, sender, is_alive, **kwargs):
        if not is_alive:
            self.logger.info("Keypad thread seems to be dead.")


    def on_view_changed(self, sender, view, **kwargs):
        pass
 
    def on_key_pressed(self, sender, col, row, btn, **kwargs):
        pass
    
    def on_barcode_read(self, sender, barcode, **kwargs):
        self.send_data_to_pages(
            pages=["page_products", "page_stocks"],
            payload={
                "type": "page_message",
                "message": f"New scanned barcode: {barcode}",
                "barcode": barcode,
            }
        )

    def on_nfc_tag_id_read(self, sender, id, **kwargs):
        self.logger.info(f"New scanned NFC Tag: {id}")
        self.send_data_to_pages(
            "page_customers",
            {
                "type": "page_message",
                "message": f"New scanned NFC Tag: {id}",
                "card_number": id,
            }
        )


    def get_target_urls(self):
        """Fetch target URLs from an environment variable."""
        # The environment variable should contain URLs separated by commas
        urls = os.getenv('TARGET_SERVICES', '')  # Example: 'http://service1:8000, http://service2:8000'
        return [url.strip() for url in urls.split(',') if url.strip()]
    
    def on_websocket_connect(self, sender, **kwargs):
       pass
    
    def on_websocket_disconnect(self, sender, **kwargs):
        pass
    # =================================================================================================================
    # Websocket posters
    # =================================================================================================================
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


    def nfc_write(self, text):
        """Simulates an NFC write."""
        #loop = asyncio.get_event_loop()
        #await loop.run_in_executor(None, self.reader.write, text)
        self.hwif.nfc_reader.write(text)

    def send_data_to_pages(self, pages, payload):
        _data_sent = {}

        if not isinstance(pages, list):
            pages = [pages]
        for page in pages:
            self.logger.debug(f"Sending data to page {page}: {payload}")
            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    page, 
                    payload,
                )
                _data_sent[page] = payload
                _data_sent[page]= 'success'
            except Exception as e:
                _data_sent[page]= 'failed'
                self.logger.error(f"Failed to send data to page {page}: {e}")

        try:
            pages_success = [page for page in _data_sent if _data_sent[page]== 'success']
            pages_failed = [page for page in _data_sent if _data_sent[page] == 'failed']
            self.logger.info(f"Data sent to pages {pages_success} ({len(pages_success)}/{len(pages)}): {payload}")
            if pages_failed:
                self.logger.error(f"Failed to send data to page {pages_failed} ({len(pages_failed)}/{len(pages)}): {payload}")
        except Exception as e:
            self.logger.error(f"Failed to log data sent to pages: {e}")

    def __del__(*args, **kwargs):
        print("HardwareController deleted.")









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


