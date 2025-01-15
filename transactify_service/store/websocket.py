import json
import uuid
import asyncio
import threading
from django.apps import AppConfig
from config.Config import Config
from django.conf import settings
import websockets


class PersistentWebSocket:
    def __init__(self, ws_url, store_config):
        self.ws_url = ws_url
        self.store_config = store_config
        self.keep_running = True

    async def connect_and_listen(self):
        """
        Establish and maintain a WebSocket connection.
        """
        while self.keep_running:
            try:
                # Connect to the WebSocket server
                print(f"Connecting to {self.ws_url}")
                async with websockets.connect(self.ws_url) as websocket:
                    # Send the store configuration
                    await websocket.send(json.dumps(self.store_config))
                    print(f"Sent store config to terminal: {self.store_config}")

                    # Listen for messages
                    while self.keep_running:
                        response = await websocket.recv()
                        print(f"Message from terminal: {response}")
            except Exception as e:
                print(f"WebSocket connection failed: {e}")
                print("Retrying in 5 seconds...")
                await asyncio.sleep(5)  # Wait before retrying

    def run_in_background(self):
        """
        Start the WebSocket connection in a new asyncio event loop running in a thread.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.connect_and_listen())

    def start(self):
        """
        Start the WebSocket connection in a background thread.
        """
        thread = threading.Thread(target=self.run_in_background, daemon=True)
        thread.start()
        print("WebSocket connection started in the background.")

    def stop(self):
        """
        Stop the WebSocket connection loop.
        """
        self.keep_running = False
