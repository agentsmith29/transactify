import time
import threading
from django.dispatch import Signal
import time

import logging
from terminal.controller.BaseHardware import BaseHardware

class NFCReaderSignals:
    tag_read = Signal()
    tag_reading_status  = Signal()
    tag_connected = Signal()
    tag_disconnected = Signal()
    nfc_tag_id_read = Signal()

class NFCBase(BaseHardware):

    def __init__(self, *args, **kwargs):
        super().__init__()
        """
        Initialize the NFCReader with signals for read and write actions.
        """
        self.logger.info(f"NFC Reader initialization.")
        self.signals = NFCReaderSignals()
        self.reading = True  # Control flag for reading process



    def start_thread(self):
        """Start the NFC reading thread."""
        self.reading = True
        self.logger.info("Creating a new thread to read NFC.")
        self._thread = threading.Thread(target=self.run)
        self._thread.daemon = True
        self._thread.start()
        self.logger.debug(f"NFC thread started with PID {self._thread.ident}")


    def run(self):
        raise NotImplementedError("The run method must be implemented in the subclass.")