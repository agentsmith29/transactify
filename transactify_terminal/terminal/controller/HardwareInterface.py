
from django.dispatch import Signal

from luma.core.interface.serial import spi
from luma.oled.device import ssd1322 as OLED
from luma.lcd.device import ili9341 as OLED
from .KeyPad import KeyPad

from .BarcodeScanner import BarcodeScanner
from .NFCReader import NFCReader
from .LEDStripController import LEDStripController

class HardwareSignals():
    pass
    #barcode_read = Signal()
    #nfc_read = Signal()
    
class HardwareInterface():

    def __init__(self):
        self.signals = HardwareSignals()

        #spi1 = spi(port = 0, device=1, gpio_DC=23, gpio_RST=24)
        #self._oled = OLED(serial_monitor)
        spi0 = spi(port = 0, device=0, gpio_DC=25, gpio_RST=12)
        self._oled = OLED(spi0, width=320, height=240, bgr=True)
       
        self._keypad = KeyPad()
        self._ledstrip = LEDStripController()

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
    
    @property
    def ledstrip(self):
        return self._ledstrip
    

    


