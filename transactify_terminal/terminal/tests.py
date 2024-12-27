from django.test import TestCase

# Create your tests here.
from unittest.mock import patch

from .controller.BarcodeScanner import BarcodeScanner
from .controller.MockSerial import AsyncMockSerial

import asyncio
import serial  # Original serial module
import pytest
from unittest.mock import MagicMock

class BarcodeReaderTests(TestCase):
    def mock_async_serial():
        mock_serial = AsyncMockSerial()
        asyncio.create_task(mock_serial._simulate_reading())  # Start the simulation
        return mock_serial

    @pytest.mark.asyncio
    async def test_barcode_reader_signal():
        # Create a mock signal handler
        mock_signal_handler = MagicMock()

        # Replace serial.Serial with MockSerial for testing
        with patch('serial.Serial', new=AsyncMockSerial):
            # Initialize the BarcodeScanner
            barcode_reader = BarcodeScanner(device_path='/dev/ttyACM0', baudrate=115200)

            # Connect the mock handler to the barcode_read signal
            barcode_reader.signals.barcode_read.connect(mock_signal_handler)

            # Allow time for the mocked serial reader to emit the signal
            await asyncio.sleep(3)  # Adjust based on the simulated delay in MockSerial

            # Assert that the signal was emitted with the correct barcode data
            mock_signal_handler.assert_called_once_with(
                sender=barcode_reader,
                barcode="1234567890"
            )