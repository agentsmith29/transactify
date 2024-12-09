
from django.dispatch import Signal

from luma.core.interface.serial import spi
from luma.oled.device import ssd1322 as OLED
from .KeyPad import KeyPad

from .BarcodeScanner import BarcodeScanner
from .NFCReader import NFCReader

class HardwareSignals():
    pass
    #barcode_read = Signal()
    #nfc_read = Signal()
    
class HardwareInterface():

    def __init__(self):
        self.signals = HardwareSignals()

        serial_monitor = spi(port = 0, device=1, gpio_DC=23, gpio_RST=24)
        self._oled = OLED(serial_monitor)
        self._keypad = KeyPad()

        # Multithreading 
        self._nfc_reader = NFCReader()
        self._barcode_reader = BarcodeScanner()
        
    # property and setters
    @property
    def nfc_reader(self):
        return self._nfc_reader
    
    @property
    def keypad(self):
        return self._keypad
    
    @property
    def oled(self):
        return self._oled
    
    @property
    def barcode_reader(self):
        return self._barcode_reader
    


