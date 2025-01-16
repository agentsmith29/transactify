"""
    This example will wait for any ISO14443A card or tag, and
    depending on the size of the UID will attempt to read from it.
   
    If the card has a 4-byte UID it is probably a Mifare
    Classic card, and the following steps are taken:
   
    - Authenticate block 4 (the first block of Sector 1) using
      the default KEYA of 0XFF 0XFF 0XFF 0XFF 0XFF 0XFF
    - If authentication succeeds, we can then read any of the
      4 blocks in that sector (though only block 4 is read here)

    If the card has a 7-byte UID it is probably a Mifare
    Ultralight card, and the 4 byte pages can be read directly.
    Page 4 is read by default since this is the first 'general-
    purpose' page on the tags.

    To enable debug message, define DEBUG in nfc/pn532_log.h
"""
import time
from pn532pi import Pn532, pn532
from pn532pi import Pn532I2c
import threading
from django.dispatch import Signal
import time
from .NFCBase import NFCBase
import binascii
import logging


# Set the desired interface to True
class PN532(NFCBase):
    # When the number after #if & #elif set as 0, it will be switch to I2C Mode
    def __init__(self, *args, **kwargs):
        # call the base class constructor
        super().__init__(*args, **kwargs)
        """
        Initialize the NFCReader with signals for read and write actions.
        """

        self.PN532_I2C = Pn532I2c(1)
        self.nfc = Pn532(self.PN532_I2C)
        
        # Start the NFC reading thread
        self.setup()
        self.start_thread()
        self.logger.info("[NFC] NFC Reader initialized.")


    def setup(self):
        self.nfc.begin()

        versiondata = self.nfc.getFirmwareVersion()
        if (not versiondata):
            print("Didn't find PN53x board")
            raise RuntimeError("Didn't find PN53x board")  # halt

        #  Got ok data, print it out!
        print("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF, (versiondata >> 16) & 0xFF,
                                                                    (versiondata >> 8) & 0xFF))
        #  configure board to read RFID tags
        self.nfc.SAMConfig()
        print("Waiting for an ISO14443A Card ...")


    def run(self):
        while self.reading:
            print("wait for a tag")
            # wait until a tag is present
            tagPresent = False
            while not tagPresent:
                time.sleep(.1)
                tagPresent, uid = self.nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)

            # if NTAG21x enables r/w protection, uncomment the following line 
            # nfc.ntag21x_auth(password)

            status, buf = self.nfc.mifareultralight_ReadPage(3)
            capacity = int(buf[2]) * 8
            print("Tag capacity {:d} bytes".format(capacity))

            for i in range(4, int(capacity/4)):
                status, buf = self.nfc.mifareultralight_ReadPage(i)
                print(binascii.hexlify(buf[:4]))

            # wait until the tag is removed
            while tagPresent:
                time.sleep(.1)
                tagPresent, uid = self.nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)

   