import threading
from .mfrc522 import SimpleMFRC522
from django.dispatch import Signal


class NFCReaderSignals:
    tag_read = Signal()


class NFCReader:
    def __init__(self):
        """
        Initialize the NFCReader with signals for read and write actions.
        """
        self.signals = NFCReaderSignals()

        self._nfc = SimpleMFRC522()

        self.reading = True  # Control flag for reading process
        self.nfc_thread = None  # Placeholder for the thread instance

        # Start the NFC reading thread
        self.start_thread()

    def start_thread(self):
        """Start the NFC reading thread."""
        self.reading = True
        self.nfc_thread = threading.Thread(target=self.run)
        self.nfc_thread.daemon = True
        self.nfc_thread.start()

    def stop_thread(self):
        """Stop the NFC reading thread."""
        self.reading = False
        if self.nfc_thread and self.nfc_thread.is_alive():
            self.nfc_thread.join()  # Wait for the thread to finish

    def run(self):
        """Continuously read NFC tags unless the process is paused."""
        while self.reading:
            try:
                id, text = self._nfc.read()
                print(f"Read from {id}: {text}")
                if self.signals.tag_read:
                    self.signals.tag_read.send(sender=self, id=id, text=text)  # Emit the read signal
            except Exception as e:
                print(f"Error during read: {e}")

    def write(self, text):
        """
        Temporarily stop reading to write to an NFC tag, then restart reading.

        Args:
            text (str): The text to write to the NFC tag.
        """
        print("Stopping reading process for writing.")
        self.stop_thread()  # Stop the thread safely

        try:
            id, _ = self._nfc.write(text)
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
        print("Stopping reading process for blocking read.")
        self.stop_thread()  # Stop the thread safely

        try:
            # Directly call the read method in a blocking manner
            id, text = self._nfc.read()
            print(f"Blocking read: {id}, {text}")
            return id, text
        except Exception as e:
            print(f"Error during blocking read: {e}")
            return None, None
        finally:
            print("Resuming reading process.")
            self.start_thread()  # Restart the thread
