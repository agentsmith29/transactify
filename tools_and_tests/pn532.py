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
import binascii

from pn532pi import Pn532, pn532
from pn532pi import Pn532I2c
from pn532pi import Pn532Spi
from pn532pi import Pn532Hsu

# Set the desired interface to True
SPI = False
I2C = True
HSU = False

if SPI:
    PN532_SPI = Pn532Spi(Pn532Spi.SS0_GPIO8)
    nfc = Pn532(PN532_SPI)
# When the number after #elif set as 1, it will be switch to HSU Mode
elif HSU:
    PN532_HSU = Pn532Hsu(Pn532Hsu.RPI_MINI_UART)
    nfc = Pn532(PN532_HSU)

# When the number after #if & #elif set as 0, it will be switch to I2C Mode
elif I2C:
    PN532_I2C = Pn532I2c(1)
    nfc = Pn532(PN532_I2C)


def setup():
    nfc.begin()

    versiondata = nfc.getFirmwareVersion()
    if (not versiondata):
        print("Didn't find PN53x board")
        raise RuntimeError("Didn't find PN53x board")  # halt

    #  Got ok data, print it out!
    print("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF, (versiondata >> 16) & 0xFF,
                                                                (versiondata >> 8) & 0xFF))

    #  configure board to read RFID tags
    nfc.SAMConfig()

    print("Waiting for an ISO14443A Card ...")


def loop():
    #  Wait for an ISO14443A type cards (Mifare, etc.).  When one is found
    #  'uid' will be populated with the UID, and uidLength will indicate
    #  if the uid is 4 bytes (Mifare Classic) or 7 bytes (Mifare Ultralight)
    for kaya_1 in (range(0xFF,-1, -1)):
        for kaya_2 in (range(0xFF, -1, -1)):
            for kaya_3 in (range(0xFF, -1, -1)):
                for kaya_4 in (range(0xFF, -1, -1)):
                    for kaya_5 in (range(0xFF, -1,-1)):
                        for kaya_6 in (range(0xFF, -1,-1)):
                            keya = bytearray([kaya_1, kaya_2, kaya_3, kaya_4, kaya_5, kaya_6])
                            success, uid = nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)

                            if (success):
                                #  Display some basic information about the card
                                print("Found an ISO14443A card")
                                print("UID Length: {:d}".format(len(uid)))
                                print("UID Value: {}".format(binascii.hexlify(uid)))

                                if (len(uid) == 4):
                                                                #  We probably have a Mifare Classic card ...
                                    print("Seems to be a Mifare Classic card (4 byte UID)")

                                    #  Now we need to try to authenticate it for read/write access
                                    #  Try with the factory default KeyA: 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF
                                    print("Trying to authenticate block 4 with default KEYA value")

                                    success = nfc.mifareclassic_AuthenticateBlock(uid, 4, 0, keya)
                                    print(f"Testing KEYA: {binascii.hexlify(keya)}")
                                    if success:
                                        print("Sector 1 (Blocks 4..7) has been authenticated")
                                        print(f"KEYA: {binascii.hexlify(keya)}")
                                        for i in range(0, 53):
                                            success, data = nfc.mifareclassic_ReadDataBlock(i)
                                            if (success):
                                                #  Data seems to have been read ... spit it out
                                                print(f"Reading Block {i}: {binascii.hexlify(data)}")
                                                return True
                                            else:
                                                print("Ooops ... unable to read the requested block.  Try another key?")
                                    else:
                                        print("Ooops ... authentication failed: Try another key?")
            print(f"No key found for {binascii.hexlify(uid)}")
            return False

    #

if __name__ == '__main__':
    setup()
    found = loop()
    while not found:
        found = loop()