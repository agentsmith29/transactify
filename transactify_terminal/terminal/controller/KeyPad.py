import RPi.GPIO as GPIO
import time
import threading
import asyncio

from django.dispatch import Signal

import logging

from .BaseHardware import BaseHardware

class KeyPadSignals:
    key_pressed = Signal()

class KeyPad(BaseHardware):

    def __init__(self):
        super().__init__(thread_disabled=False)
        #if not self.thread_disabled:
        # Define GPIO pin mappings based on the schematic
        self.columns = self.global_config.keypad.KEYPAD_COLS
        self.rows = self.global_config.keypad.KEYPAD_ROWS
        self.logger.info(f"KeyPad initialization. KeyPad using GPIOS { self.global_config.keypad.KEYPAD_ROWS} and {self.rows}")

        # Define the keypad layout based on the schematic
        self.keypad = [
            ['1', '2', '3', 'A'],
            ['4', '5', '6', 'B'],
            ['7', '8', '9', 'C'],
            ['0', 'F', 'E', 'D']
        ]
        self.signals = KeyPadSignals()
        self.reading = True
        self.start_thread()
        #else:
        #    self.logger.warning("KeyPad thread disabled. Not starting thread.")

    def start_thread(self): 
        if super().start_thread():
            self.logger.debug("Creating a new thread to read keypad.")
            self._thread = threading.Thread(target=self.run_thread, daemon=True)
            self._thread.start()
            self.logger.info(f"KeyPad thread started with PID {self._thread.ident}")
        

    def setup(self):
        self.logger.debug("Setting up GPIOs for KeyPad.")
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

        self.logger.info("Setup complete for keypad complete. Ready to read keypad.")
        self.abort_cnt = 0

    def run(self) -> str:
        for i, col in enumerate(self.columns):
            GPIO.output(col, GPIO.LOW)  # Drive one column low
            for j, row in enumerate(self.rows):
                if GPIO.input(row) == GPIO.LOW:  # Check if any row is low
                    self.logger.debug(f"Button pressed: {self.keypad[j][i]} Column {col}. Row {row}.")
                    #print(f"[KeyPad] Button pressed: {self.keypad[j][i]} COL {col}. ROW {row}")
                    self.signals.key_pressed.send(sender=self, col=col, row=row, btn=self.keypad[j][i])  # Emit the read signal
                    time.sleep(0.5)
            GPIO.output(col, GPIO.HIGH)  # Set the column back to high
            time.sleep(0.01)

    def cleanup(self):
        self.logger.info("Cleaning up GPIOs for KeyPad.")
        GPIO.cleanup()
        return super().cleanup()

    def __del__(self):
        self.logger.info("Exiting Application. Cleaning up GPIOs.")
        self.cleanup()



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