from evdev import InputDevice, categorize, ecodes


class BarcodeScanner:
    """
    A class to encapsulate barcode/keypad reading from a specific HID device.
    """
    def __init__(self, hid_device_path, message_handler):
        """
        Initialize the KeypadReader.

        Args:
            hid_device_path (str): Path to the HID device (e.g., /dev/input/eventX).
            message_handler (callable): A function to handle the completed input.
        """
        self.hid_device_path = hid_device_path
        self.message_handler = message_handler
        self.device = None
        self.barcode = ""  # Buffer to store the barcode/input
        self.key_pressed = False  # Track if a key is currently pressed

    def start(self):
        """Start reading from the HID device."""
        try:
            # Open the HID device
            self.device = InputDevice(self.hid_device_path)
            print(f"Listening for keypad input on {self.device.name} ({self.hid_device_path})")

            # Start processing events
            self._process_events()

        except FileNotFoundError:
            print(f"Error: Device not found at {self.hid_device_path}")
        except Exception as e:
            print(f"Error initializing KeypadReader: {e}")

    def _process_events(self):
        """Process input events from the HID device."""
        try:
            for event in self.device.read_loop():
                if event.type == ecodes.EV_KEY:  # Only process key events
                    key_event = categorize(event)

                    if key_event.keystate == key_event.key_down and not self.key_pressed:
                        # Process the key only if no key is currently pressed
                        self.key_pressed = True
                        key = key_event.keycode

                        if key == "KEY_ENTER":  # Barcode ends with Enter
                            if self.barcode:  # Process only if buffer is not empty
                                print(f"Received complete input: {self.barcode}")
                                self.message_handler(self.barcode)  # Handle the barcode/input
                                self.barcode = ""  # Reset buffer for the next input
                        elif key.startswith("KEY_") and len(key) > 4:
                            # Map keys to characters (e.g., KEY_1 -> '1', KEY_A -> 'A')
                            char = key[-1] if key[-1].isdigit() else key[-1].lower()
                            self.barcode += char

                    elif key_event.ke
