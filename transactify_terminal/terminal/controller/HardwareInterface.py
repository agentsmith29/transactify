
from django.dispatch import Signal

from luma.core.interface.serial import spi
from luma.oled.device import ssd1322 as OLED
#from luma.lcd.device import ili9341 as OLED
from .KeyPad import KeyPad

from .BarcodeScanner import BarcodeScanner
from .NFC.MFRC522 import MFRC522 as NFCReader
from .NFC.PN532 import PN532 as PN532
from .LEDStripController import LEDStripController
from .BaseHardware import BaseHardware
import threading
import time
import logging
from transactify_terminal.settings import CONFIG

class HardwareInterfaceSignals():
    pass
    keypad_thread_status = Signal()
    nfc_thread_status = Signal()
    barcode_thread_status = Signal()


    #nfc_read = Signal()
    
class HardwareInterface():

    def __init__(self):
        self.logger = logging.getLogger(f"{CONFIG.webservice.SERVICE_NAME}.{self.__class__.__name__}")
        self.signals = HardwareInterfaceSignals()

        spi1 = spi(port = 0, device=1, gpio_DC=23, gpio_RST=24)
        self._oled = OLED(spi1)
        #spi0 = spi(port = 0, device=0, gpio_DC=25, gpio_RST=12)
        #self._oled = OLED(spi0, width=320, height=240, bgr=True)
       
        self._keypad = KeyPad()

        self._ledstrip = LEDStripController()

        # Multithreading 
        # self._nfc_reader = NFCReader()
        self._nfc_reader2 = PN532()

        self._barcode_reader = BarcodeScanner()

        self._abort_thread = False
        self._thread = threading.Thread(target=self.hardware_thread_watchdog, daemon=True)
        self._thread.start()
        


    def hardware_thread_watchdog(self, auto_restart=True):
        """ Monitor all hardware threads print a message if any of them are not running """
        self._keypad_thread = self._keypad.thread
        self._nfc_thread = self._nfc_reader2.thread
        self._barcode_thread = self._barcode_reader.thread
        while not self._abort_thread:
            for inst, signal in zip(
                    [self._keypad, self._nfc_reader2, self._barcode_reader],
                    [self.signals.keypad_thread_status, self.signals.nfc_thread_status, self.signals.barcode_thread_status]
                ):
                if inst.thread_disabled:
                    continue 

                if inst.thread is None or (isinstance(inst.thread, threading.Thread) and not inst.thread.is_alive()):
                    signal.send(sender=self, is_alive=False) 
                  
                    if inst.restart_counter < inst.max_restarts:
                        inst.start_thread()  
                    else:
                        self.logger.error(f"Thread {inst} has reached the maximum restarts.")
                        inst.thread_disabled = True
                    inst.restart_counter += 1
                else:
                    self.signals.keypad_thread_status.send(sender=self, is_alive=inst.thread.is_alive())
                time.sleep(1)



    # property and setters
    @property
    def nfc_reader(self) -> NFCReader:
        return self._nfc_reader2
    
    @property
    def keypad(self) -> KeyPad:
        return self._keypad
    
    @property
    def oled(self) -> OLED:
        return self._oled
    
    @property
    def barcode_reader(self) -> BarcodeScanner:
        return self._barcode_reader
    
    @property
    def ledstrip(self) -> LEDStripController:
        return self._ledstrip
    

    


