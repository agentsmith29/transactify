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
        self.start_thread()


    def setup(self):
        self.nfc.begin()

        versiondata = self.nfc.getFirmwareVersion()
        if (not versiondata):
            self.logger.error("Didn't find PN53x board")
            raise RuntimeError("Didn't find PN53x board")  # halt

        #  Got ok data, print it out!
        self.logger.info("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF, (versiondata >> 16) & 0xFF,
                                                                    (versiondata >> 8) & 0xFF))
        #  configure board to read RFID tags
        self.nfc.SAMConfig()
        self.logger.info(f"Setup for NFC Reader {self.nfc} completed.")

    def _uid_to_num(self, uid):
        n = 0
        for i in range(0, len(uid)):
            n = n * 256 + uid[i]
        return n
    
    def run(self):
        self.setup()
        while self.reading:
            self.logger.info("Waiting for an ISO14443A Card ...")
            # wait until a tag is present
            tagPresent = False
            while not tagPresent:
                time.sleep(.1)
                tagPresent, uid = self.nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)
            self.logger.debug("NFC card or tag detected.")

            self.signals.tag_reading_status.send(sender=self, status=1)
            self.logger.info(f"Tag UID: {self._uid_to_num(uid)} [0x{binascii.hexlify(uid)}] ")
            # if NTAG21x enables r/w protection, uncomment the following line 
            # nfc.ntag21x_auth(password)
            try:
                self.signals.tag_reading_status.send(sender=self, status=3)
                self.signals.nfc_tag_id_read.send(sender=self, id=self._uid_to_num(uid))
                # wait until the tag is removed
                while tagPresent:
                    time.sleep(.1)
                    tagPresent, uid = self.nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)
                    self.signals.tag_reading_status.send(sender=self, status=4)
            except Exception as e:
                self.logger.error(f"Error reading NFC tag: {e}")

            self.logger.debug(f"Tag was removed.")

    def read_mifare_ultralight(self,):
        #  We probably have a Mifare Ultralight card ...
        print("Seems to be a Mifare Ultralight tag (7 byte UID)")

        #  Try to read the first general-purpose user page (#4)
        print("Reading page 4")
        success, data = self.nfc.mifareultralight_ReadPage(4)
        if (success):
            #  Data seems to have been read ... spit it out
            binascii.hexlify(data)
            return True

        else:
            print("Ooops ... unable to read the requested page!?")

    def read_mifarce_classic(self, success, uid ):
        authenticated = False               # Flag to indicate if the sector is authenticated

        # Keyb on NDEF and Mifare Classic should be the same
        keyuniversal = bytearray([ 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF ])

        # Wait for an ISO14443A type cards (Mifare, etc.).  When one is found
        # 'uid' will be populated with the UID, and uidLength will indicate
        # if the uid is 4 bytes (Mifare Classic) or 7 bytes (Mifare Ultralight)

        if (success):
            # Display some basic information about the card
            print("Found an ISO14443A card")
            print("UID Length: {:d}".format(len(uid)))
            print("UID Value: {}".format(binascii.hexlify(uid)))

            if (len(uid) == 4):
                # We probably have a Mifare Classic card ...
                print("Seems to be a Mifare Classic card (4 byte UID)")

                # Now we try to go through all 16 sectors (each having 4 blocks)
                # authenticating each sector, and then dumping the blocks
                for currentblock in range(64):
                    # Check if this is a new block so that we can reauthenticate
                    if (self.nfc.mifareclassic_IsFirstBlock(currentblock)):
                        authenticated = False

                    # If the sector hasn't been authenticated, do so first
                    if (not authenticated):
                        # Starting of a new sector ... try to to authenticate
                        print("------------------------Sector {:d}-------------------------".format(int(currentblock / 4)))
                        if (currentblock == 0):
                            # This will be 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF for Mifare Classic (non-NDEF!)
                            # or 0xA0 0xA1 0xA2 0xA3 0xA4 0xA5 for NDEF formatted cards using key a,
                            # but keyb should be the same for both (0xFF 0xFF 0xFF 0xFF 0xFF 0xFF)
                            success = self.nfc.mifareclassic_AuthenticateBlock (uid, currentblock, 1, keyuniversal)
                        else:
                            # This will be 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF for Mifare Classic (non-NDEF!)
                            # or 0xD3 0xF7 0xD3 0xF7 0xD3 0xF7 for NDEF formatted cards using key a,
                            # but keyb should be the same for both (0xFF 0xFF 0xFF 0xFF 0xFF 0xFF)
                            success = self.nfc.mifareclassic_AuthenticateBlock (uid, currentblock, 1, keyuniversal)
                        if (success):
                            authenticated = True
                        else:
                            print("Authentication error")
                    # If we're still not authenticated just skip the block
                    if (not authenticated):
                        print("Block {:d}".format(currentblock))
                        print(" unable to authenticate")
                    else:
                        # Authenticated ... we should be able to read the block now
                        # Dump the data into the 'data' array
                        success, data = self.nfc.mifareclassic_ReadDataBlock(currentblock)

                    if (success):
                        # Read successful
                        print("Block {:d}".format(currentblock))
                        if (currentblock < 10):
                            print("  ")
                        else:
                            print(" ")
                        # Dump the raw data
                        print(binascii.hexlify(data))
                    else:
                        # Oops ... something happened
                        print("Block {:d}".format(currentblock))
                        print(" unable to read this block")
                else:
                    print("Ooops ... this doesn't seem to be a Mifare Classic card!")
                    