import time
import threading
from django.dispatch import Signal
import time

import logging


class NFCReaderSignals:
    tag_read = Signal()
    tag_reading_status  = Signal()
    tag_connected = Signal()
    tag_disconnected = Signal()
    nfc_tag_id_read = Signal()

class NFCBase():

    def __init__(self, *args, **kwargs):
        """
        Initialize the NFCReader with signals for read and write actions.
        """
        self.logger = logging.getLogger('store')
        self.logger.info(f"[NFC] NFC Reader initialization.")

        self.signals = NFCReaderSignals()

        self.reading = True  # Control flag for reading process
        self.nfc_thread = None  # Placeholder for the thread instance



    def start_thread(self):
        """Start the NFC reading thread."""
        self.reading = True
        self.logger.info("[NFC] Creating a new thread to read NFC.")
        self.nfc_thread = threading.Thread(target=self.run)
        self.nfc_thread.daemon = True
        self.nfc_thread.start()
        self.logger.debug(f"[NFC] NFC thread started with PID {self.nfc_thread.ident}")

    def stop_thread(self):
        """Stop the NFC reading thread."""
        self.logger.info("[NFC] Requesting NFC thread to stop.")
        self.reading = False
        if self.nfc_thread and self.nfc_thread.is_alive():
            self.nfc_thread.join()  # Wait for the thread to finish
        self.logger.info("[NFC] NFC thread stopped.")
        print("Endless thread stopped.")

    def run(self):
        raise NotImplementedError("The run method must be implemented in the subclass.")