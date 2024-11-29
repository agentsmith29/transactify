import RPi.GPIO as GPIO
import time
import threading
import asyncio

from django.dispatch import Signal

class KeyPadSignals:
    key_pressed = Signal()

class KeyPad():

    def __init__(self):
        # Define GPIO pin mappings based on the schematic
        self.columns = [19, 13, 6, 5]  # COL4, COL3, COL2, COL1
        self.rows = [22, 27, 17, 26]   # ROW4, ROW3, ROW2, ROW1

        # Define the keypad layout based on the schematic
        self.keypad = [
            ['1', '2', '3', 'A'],
            ['4', '5', '6', 'B'],
            ['7', '8', '9', 'C'],
            ['0', 'F', 'E', 'D']
        ]

        self.signals = KeyPadSignals()

        self.reading = True
        self.keypad_thread = threading.Thread(target=self.read_keypad)
        self.keypad_thread.daemon = True
        self.keypad_thread.start()

    def setup(self):
        # Setup GPIO mode
        GPIO.setmode(GPIO.BCM)

        # Setup row pins as inputs with pull-up resistors
        for row in self.rows:
            print(f"setup pin {row}")
            GPIO.setup(row, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            #GPIO.add_event_detect(row, GPIO.BOTH, callback=read_keypad, bouncetime=300)

        # Setup column pins as outputs
        for col in self.columns:
            GPIO.setup(col, GPIO.OUT)
            GPIO.output(col, GPIO.HIGH)  # Set columns to high initially


    def read_keypad(self) -> str:
        self.setup()
        while True:
            for i, col in enumerate(self.columns):
                GPIO.output(col, GPIO.LOW)  # Drive one column low
                for j, row in enumerate(self.rows):
                    if GPIO.input(row) == GPIO.LOW:  # Check if any row is low
                        print(f"Button pressed: {self.keypad[j][i]} COL {col}. ROW {row}")
                        self.signals.key_pressed.send(sender=self, col=col, row=row, btn=self.keypad[j][i])  # Emit the read signal
                        time.sleep(0.3)
                        #return self.keypad[j][i]
                GPIO.output(col, GPIO.HIGH)  # Set the column back to high
                time.sleep(0.1)
                #await asyncio.sleep(0.1)
        return None
    
    def __del__(self):
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