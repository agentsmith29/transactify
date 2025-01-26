import json
import uuid
import asyncio
import threading
from django.apps import AppConfig
from config.Config import Config
from django.conf import settings
import websockets
from transactify_service.settings import CONFIG
import logging

# class PersistentWebSocket:
#     def __init__(self, ws_url, store_config):
        
#         self.logger = logging.getLogger(f'{CONFIG.webservice.SERVICE_NAME}.websocket')
#         self.ws_url = ws_url
#         self.store_config = store_config
#         self.keep_running = True

#     async def connect_and_listen(self):
#         """
#         Establish and maintain a WebSocket connection.
#         """
#         while self.keep_running:
#             try:
#                 # Connect to the WebSocket server
#                 self.logger.info(f"Connecting to {self.ws_url}")
#                 async with websockets.connect(self.ws_url) as websocket:
#                     # Send the store configuration
#                     await websocket.send(json.dumps(self.store_config))
#                     self.logger.debug(f"Sent store config to terminal: {self.store_config}")

#                     # Listen for messages
#                     while self.keep_running:
#                         response = await websocket.recv()
#                         self.logger.debug(f"Message from terminal: {response}")
#             except Exception as e:
#                 self.logger.debug(f"WebSocket connection failed: {e}. Retrying in 5 seconds...")
#                 await asyncio.sleep(5)  # Wait before retrying

#     def run_in_background(self):
#         """
#         Start the WebSocket connection in a new asyncio event loop running in a thread.
#         """
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         loop.run_until_complete(self.connect_and_listen())

#     def start(self):
#         """
#         Start the WebSocket connection in a background thread.
#         """
#         thread = threading.Thread(target=self.run_in_background, daemon=True)
#         thread.start()
#         self.logger.info("WebSocket connection started in the background.")

#     def stop(self):
#         """
#         Stop the WebSocket connection loop.
#         """
#         self.keep_running = False



class PersistentWebSocket:
    def __init__(self, ws_url, store_config):
        self.logger = logging.getLogger(f'{CONFIG.webservice.SERVICE_NAME}.websocket')
        self.ws_url = ws_url
        self.store_config = store_config
        self.keep_running = True
        self.check_interval = 10  # Interval in seconds to check connection status

    async def connect_and_listen(self):
        """
        Establish and maintain a WebSocket connection.
        Periodically check the connection and retry if necessary.
        """
        while self.keep_running:
            try:
                self.logger.info(f"Connecting to {self.ws_url}")
                async with websockets.connect(self.ws_url) as websocket:
                    await websocket.send(json.dumps(self.store_config))
                    self.logger.debug(f"Sent store config to terminal: {self.store_config}")
                    
                    # Periodically send pings to keep the connection alive
                    while self.keep_running:
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=self.check_interval)
                            self.logger.debug(f"Message from terminal: {response}")
                        except asyncio.TimeoutError:
                            self.logger.info("No messages received; sending ping to keep connection alive.")
                            await websocket.ping()  # Send ping to maintain connection
                        except websockets.ConnectionClosed:
                            self.logger.warning("Connection closed unexpectedly. Reconnecting...")
                            break
            except Exception as e:
                self.logger.error(f"WebSocket connection failed: {e}. Retrying in 5 seconds...")
                await asyncio.sleep(5)

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
        self.logger.info("WebSocket connection started in the background.")

    def stop(self):
        """
        Stop the WebSocket connection loop.
        """
        self.keep_running = False
