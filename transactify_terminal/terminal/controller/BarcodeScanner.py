from evdev import InputDevice, categorize, ecodes
import serial
import threading

from django.core.signals import setting_changed
from django.dispatch import Signal


class BarcodeScannerSignals():
    barcode_read = Signal()

class BarcodeScanner:
    """
    A class to encapsulate barcode/keypad reading from a specific HID device.
    """
    def __init__(self):
        self.signals = BarcodeScannerSignals()
       
        scanner_thread  = threading.Thread(target=self.read_barcodes, daemon=True)
        scanner_thread.start()

    
    # Define the threaded function to read barcodes and broadcast them
    def read_barcodes(self):
        # Open the serial connection
        try:
            ser = serial.Serial('/dev/ttyACM0', 
                                baudrate=115200, 
                                bytesize=serial.EIGHTBITS,
                                parity=serial.PARITY_NONE,
                                stopbits=serial.STOPBITS_ONE,
                                timeout=1)  # Adjust the port and baud rate
            print("Serial connection established")
        except serial.SerialException as e:
            print(f"Error connecting to serial port: {e}")
            return

        buffer = ""  # Temporary storage for incoming data
        
        while True:
            try:
                # Read raw bytes from the serial port
                raw_data = ser.read(ser.in_waiting or 1).decode('utf-8')
                if raw_data:
                    buffer += raw_data  # Append incoming data to the buffer
                    
                    if '\r' in buffer and '\n' in buffer:
                        line = "".join(buffer.splitlines())  # Remove newline characters
                        line = line.strip()  # Remove leading/trailing whitespace
                        
                        if line:  # Ensure the line is not empty
                            print(f"Received complete barcode: {line}")
                            self.signals.barcode_read.send(sender=self, barcode=line)
                            #HardwareController.send_message_to_manage_clients(line)
                            buffer = ""  # Clear the buffer
                            line = ""
                            barcode = ""
                            

            except serial.SerialException as e:
                print(f"Serial error: {e}")
                #break  # Exit if there's a serial connection issue

            except Exception as e:
                print(f"Error processing data: {e}")

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
