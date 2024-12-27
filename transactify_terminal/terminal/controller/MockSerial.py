import asyncio
from unittest.mock import MagicMock

class AsyncMockSerial:
    def __init__(self, *args, **kwargs):
        self.in_waiting = 0
        self.data_buffer = b""
        self.is_open = True

    async def _simulate_reading(self):
        while self.is_open:
            await asyncio.sleep(2)  # Simulate delay between barcode scans
            barcode = f"1234567890\r\n"  # Simulated barcode
            self.data_buffer += barcode.encode('utf-8')
            self.in_waiting = len(self.data_buffer)

    def read(self, size=1):
        if len(self.data_buffer) == 0:
            return b""

        data = self.data_buffer[:size]
        self.data_buffer = self.data_buffer[size:]
        self.in_waiting = len(self.data_buffer)
        return data

    def close(self):
        self.is_open = False

    def __del__(self):
        self.close()
