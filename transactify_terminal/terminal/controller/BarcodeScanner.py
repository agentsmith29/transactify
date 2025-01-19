from evdev import InputDevice, categorize, ecodes
import serial
import threading

from django.core.signals import setting_changed
from django.dispatch import Signal
from .BaseHardware import BaseHardware

class BarcodeScannerSignals():
    barcode_read = Signal()

class BarcodeScanner(BaseHardware):
    """
    A class to encapsulate barcode/keypad reading from a specific HID device.
    """
    def __init__(self,  
                 device_path: str = '/dev/ttyACM0',
                 baudrate: int = 115200,
                 bytesize: int = serial.EIGHTBITS,
                 parity: int = serial.PARITY_NONE,
                 stopbits: int = serial.STOPBITS_ONE,
                 timeout: int = 1):
        super().__init__(thread_disabled=False)
        
        self.signals = BarcodeScannerSignals()
        self.buffer = ""  # Temporary storage for incoming data     
        self.start_thread()

    def start_thread(self):
        if super().start_thread():
            self.logger.debug("Creating a new thread to read the Barcode Scanner.")
            self._thread  = threading.Thread(target=self.run_thread, daemon=True)
            self._thread.start()
            self.logger.info(f"BarCode Scanner thread started with PID {self._thread.ident}")


    # Define the threaded function to read barcodes and broadcast them
    def setup(self):
        try:
            self.logger.info(f"Connecting to serial port {self.global_config.barcode_reader.DEVICE_PATH}, "
                             f"Baudrate: {self.global_config.barcode_reader.BAUDRATE}, Bytesize: {self.global_config.barcode_reader.BYTESIZE}, "
                             f"Parity: {self.global_config.barcode_reader.PARITY}, stoppbit: {self.global_config.barcode_reader.STOPBITS}, "
                             f"Timeout: {self.global_config.barcode_reader.TIMEOUT}")
            self.ser: serial.Serial = serial.Serial(
                self.global_config.barcode_reader.DEVICE_PATH,
                baudrate=self.global_config.barcode_reader.BAUDRATE,
                bytesize=self.global_config.barcode_reader.BYTESIZE,
                parity=self.global_config.barcode_reader.PARITY,
                stopbits=self.global_config.barcode_reader.STOPBITS,
                timeout=self.global_config.barcode_reader.TIMEOUT
            )
            self.logger.info(f"Serial connection established on port {self.global_config.barcode_reader.DEVICE_PATH}")
        except serial.SerialException as e:
            self.logger.error(f"Error connecting to serial port {self.global_config.barcode_reader.DEVICE_PATH}: {e}")
            return

    def run(self):
        try:
            # Read raw bytes from the serial port
            raw_data = self.ser.read(self.ser.in_waiting or 1).decode('utf-8')
            if raw_data:
                self.buffer += raw_data  # Append incoming data to the buffer
                
                if '\r' in buffer and '\n' in buffer:
                    line = "".join(buffer.splitlines())  # Remove newline characters
                    line = line.strip()  # Remove leading/trailing whitespace
                    
                    if line:  # Ensure the line is not empty
                        self.logger.debug(f"Received complete barcode: {line}")
                        self.signals.barcode_read.send(sender=self, barcode=line)
                        #HardwareController.send_message_to_manage_clients(line)
                        buffer = ""  # Clear the buffer
                        line = ""
                        barcode = ""
        except serial.SerialException as e:
            self.logger.error(f"Serial error on port {self.global_config.barcode_reader.DEVICE_PATH}: {e}")
        except Exception as e:
            self.logger.error(f"Error on port {self.global_config.barcode_reader.DEVICE_PATH}: {e}")




    def read_barcode_stdin(self):
        try:
            # Open the HID device
            device = InputDevice('/dev/input/event4')  # Adjust the event number
            #print(f"Listening for barcodes on {device.name} ({hid_device_path})")

            barcode = ""  # Buffer for building the barcode
            key_pressed = False  # Track if a key is currently pressed

            # Loop to read events
            for event in device.read_loop():
                if event.type == ecodes.EV_KEY:  # Only process key events
                    key_event = categorize(event)

                    if key_event.keystate == key_event.key_down and not key_pressed:
                        # Process the key only if no key is currently pressed
                        #print(f"Key: {key_event.keycode}")
                        key_pressed = True
                        key = key_event.keycode

                        if key == "KEY_ENTER":  # Barcode ends with Enter
                            if barcode:  # Only process if buffer is not empty
                                print(f"Received barcode: {barcode}")
                                if self.current_view == "view_main":
                                    # Get the product name and price from the database
                                    try:
                                        product = Product.objects.filter(ean=barcode).first()
                                        self.view_price(product.name, product.resell_price)
                                        # read nfc
                                        id, text = self.nfc_read()
                                        print(f"Received NFC: {id}")
                                    except Exception as e:
                                        print(f"Error fetching product: {e}")
                                else:
                                    print(f"Barcode received, but not in the main view {self.current_view}")
                                    #HardwareController.send_message_to_manage_clients(barcode)  # Send barcode
                                    self.barcode_read.send(sender=self, barcode=barcode)
                                barcode = ""  # Reset buffer
                        elif key.startswith("KEY_") and len(key) > 4:
                            if key == "KEY_NUMLOCK" or key == "KEY_DOWN":
                                continue
                            #else:
                            #    print(f"Key: {key}")
                            # Map keys to characters (e.g., KEY_1 -> '1')
                            char = key[-1] if key[-1].isdigit() else key[-1].lower()
                            barcode += char

                    elif key_event.keystate == key_event.key_up:
                        # Reset the key_pressed state on key release
                        key_pressed = False

        except KeyboardInterrupt:
            print("\nStopping barcode reader...")
        except Exception as e:
            print(f"Error: {e}")

    def send_directly(self, barcode):
        self.signals.barcode_read.send(sender=self, barcode=barcode)
        print(f"Sent barcode directly: {barcode}")