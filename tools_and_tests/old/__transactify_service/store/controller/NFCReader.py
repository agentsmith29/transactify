import threading
from .mfrc522 import SimpleMFRC522, MFRC522
from django.dispatch import Signal
import time

import logging

class NFCReaderSignals:
    tag_read = Signal()
    tag_reading_status  = Signal()


class NFCReader:
    def __init__(self):
        """
        Initialize the NFCReader with signals for read and write actions.
        """
        self.logger = logging.getLogger('store')
        self.logger.info(f"[NFC] NFC Reader initialization.")

        self.signals = NFCReaderSignals()

        self._reader = MFRC522()
        #self._reader = SimpleMFRC522()

        self.reading = True  # Control flag for reading process
        self.nfc_thread = None  # Placeholder for the thread instance

        # Start the NFC reading thread
        self.start_thread()

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

    def read(self, reader: MFRC522, trailer_block, key, block_addrs):
        
        (status, TagType) = reader.Request(self._reader.PICC_REQIDL)
        if status != reader.MI_OK:
            return None, None
        else:
            self.logger.debug(f"[NFC] Card detected and connected. Type: {str(TagType)}")
            self.signals.tag_reading_status.send(sender=self, status=1)
        
        (status, uid) = reader.Anticoll()
        if status != reader.MI_OK:
            return None, None
        else:
            self.logger.info(f"[NFC] Card read UID: {uid}")
            self.signals.tag_reading_status.send(sender=self, status=2)

        id = self._uid_to_num(uid)
        reader.SelectTag(uid)
        status = reader.Authenticate(reader.PICC_AUTHENT1A, trailer_block , key, uid)
        
        data = []
        text_read = ''
        if status == reader.MI_OK:
            self.logger.debug("[NFC] Reading data from block...")
            self.signals.tag_reading_status.send(sender=self, status=3)
            for block_num in block_addrs:
                block = reader.ReadTag(block_num)
                if block:
                    data += block
            if data:
                text_read = ''.join(chr(i) for i in data)
            self.logger.debug(f"[NFC] Data read from {id}: {text_read}")
        reader.StopAuth()
        self.signals.tag_reading_status.send(sender=self, status=4)
        self.logger.info(f"[NFC] Card {id} disconnected.")
        
        return id, text_read
    
    def _uid_to_num(self, uid):
        n = 0
        for i in range(0, 5):
            n = n * 256 + uid[i]
        return n
    
    def run(self):
        """Continuously read NFC tags unless the process is paused."""
        while self.reading:
        #try:
            trailer_block = 11
            key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
            block_addrs = [8,9,10]
            id, text = self.read(self._reader, trailer_block, key, block_addrs)
            if id is None:
                continue
            #id, text = self._reader.read()
            self.logger.debug("[NFC] Card {id}. Content: {text}")
            if self.signals.tag_read:
                self.signals.tag_read.send(sender=None, id=id, text=text)  # Emit the read signal
                time.sleep(5)
        #except Exception as e:
        #    print(f"Error during read: {e}")

    def write(self, text):
        """
        Temporarily stop reading to write to an NFC tag, then restart reading.

        Args:
            text (str): The text to write to the NFC tag.
        """
        self.logger.info("[NFC] Stopping reading process for writing.")
        self.stop_thread()  # Stop the thread safely

        try:
            id = None
            trailer_block = 11
            key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
            block_addrs = [8,9,10]
            while id is None:
                id, text = self.read(self._reader, trailer_block, key, block_addrs)
            print(f"Written to {id}: {text}")
        except Exception as e:
            print(f"Error during write: {e}")
        finally:
            print("Resuming reading process.")
            self.start_thread()  # Restart the thread

    def read_block(self):
        """
        Stop the reading loop, perform a blocking read, then restart the loop.

        Returns:
            tuple: The ID and text read from the NFC tag.
        """
        self.logger.info("[NFC] Stopping reading process for blocking read.")
        self.stop_thread()  # Stop the thread safely

        try:
            # Directly call the read method in a blocking manner
            id = None
            trailer_block = 11
            key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
            block_addrs = [8, 9, 10]
            while id is None:
                id, text = self.read(self._reader, trailer_block, key, block_addrs)
            self.logger.info("[NFC] Blocking read complete. Card {id}. Content: {text}")
            return id, text
        except Exception as e:
            self.logger.error(f"[NFC] Error during blocking read: {e}")
            return None, None
        finally:
            self.logger.info("Resuming reading process.")
            self.start_thread()  # Restart the thread
