import RPi.GPIO as GPIO
import time
import threading
import asyncio

from django.dispatch import Signal

import logging

class KeyPadSignals:
    key_pressed = Signal()

class KeyPad():

    def __init__(self):
        self.logger = logging.getLogger('store')
        self.logger.info(f"KeyPad initialization.")
        # Define GPIO pin mappings based on the schematic
        self.columns = [19, 13, 6, 5]  # COL4, COL3, COL2, COL1
        self.rows = [22, 27, 17, 26]   # ROW4, ROW3, ROW2, ROW1
        self.logger.debug(f"KeyPad using GPIOS {self.columns} and {self.rows}")

        # Define the keypad layout based on the schematic
        self.keypad = [
            ['1', '2', '3', 'A'],
            ['4', '5', '6', 'B'],
            ['7', '8', '9', 'C'],
            ['0', 'F', 'E', 'D']
        ]
        

        self.signals = KeyPadSignals()

        self.reading = True
        self.logger.info("[KeyPad] Creating a new thread to read keypad.")
        self.keypad_thread = threading.Thread(target=self.read_keypad)
        self.keypad_thread.daemon = True
        self.keypad_thread.start()
        self.logger.debug(f"[KeyPad] KeyPad thread started with PID {self.keypad_thread.ident}")

    def setup(self):
        # Setup GPIO mode
        GPIO.setmode(GPIO.BCM)

        # Setup row pins as inputs with pull-up resistors
        for row in self.rows:
            # self.logger.debug(f"[KeyPad] Setup GPIO Row-Pin {row}.")
            try:
                GPIO.setup(row, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            except Exception as e:
                self.logger.error(f"Error setting up GPIO Pin {row}. {e}")
            #GPIO.add_event_detect(row, GPIO.BOTH, callback=read_keypad, bouncetime=300)

        # Setup column pins as outputs
        for col in self.columns:
            # self.logger.debug(f"[KeyPad] Setup GPIO Column-Pin {row}.")
            try:
                GPIO.setup(col, GPIO.OUT)
                GPIO.output(col, GPIO.HIGH)  # Set columns to high initially
            except Exception as e:
                self.logger.error(f"Error setting up GPIO Pin {row}. {e}")

        self.logger.info("[KeyPad] Setup complete. Ready to read keypad.")

    def read_keypad(self) -> str:
        self.setup()
        while True:
            for i, col in enumerate(self.columns):
                GPIO.output(col, GPIO.LOW)  # Drive one column low
                for j, row in enumerate(self.rows):
                    if GPIO.input(row) == GPIO.LOW:  # Check if any row is low
                        self.logger.debug(f"[KeyPad] Button pressed: {self.keypad[j][i]} COL {col}. ROW {row}")
                        #print(f"[KeyPad] Button pressed: {self.keypad[j][i]} COL {col}. ROW {row}")
                        self.signals.key_pressed.send(sender=self, col=col, row=row, btn=self.keypad[j][i])  # Emit the read signal
                        time.sleep(0.5)
                GPIO.output(col, GPIO.HIGH)  # Set the column back to high
                time.sleep(0.01)
        return None
    
    def __del__(self):
        self.logger.info("[KeyPad] Exiting Application. Cleaning up GPIOs.")
        GPIO.cleanup()



    # Function to read keypad and output the pressed key

if __name__ == "__main__":
    try:
        while True:
            read_keypad()
            #print('waitin...')
            #time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting program")

    finally:
        GPIO.cleanup()