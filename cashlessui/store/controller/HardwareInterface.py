
from luma.core.interface.serial import spi
from luma.oled.device import ssd1322 as OLED
from .KeyPad import KeyPad
from .mfrc522.SimpleMFRC522 import SimpleMFRC522

class HardwareInterface():

    def __init__(self):
        serial_monitor = spi(port = 0, device=1, gpio_DC=23, gpio_RST=24)
        self._nfc_reader = SimpleMFRC522()
        self._keypad = KeyPad()
        self._oled = OLED(serial_monitor)
        
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


