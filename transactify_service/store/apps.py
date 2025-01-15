from django.apps import AppConfig
import os
import logging
from config.Config import Config
from django.conf import settings
import asyncio
import websockets
import json

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

    def stop(self):
        """
        Stop the WebSocket connection loop.
        """
        self.keep_running = False


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        # Set the store name from environment variables
        StoreConfig.store_name = os.getenv('SERVICE_NAME', 'Default Store Name')

        if os.environ.get('RUN_SERVER', 'false') == 'true':
            import store.StoreLogsDBHandler  # Import your custom logging here
            from store.data_generators.add_historical_data import HistoricalData

            # Set up custom logging
            logger = store.StoreLogsDBHandler.setup_custom_logging('apps')

        if os.environ.get('INIT_DATA', '0') == '1':
            try:
                HistoricalData()
            except Exception as e:
                logger.error(f"Failed to mock store content: {e}")

        # WebSocket configuration
        print(f"Push store name to terminal: {StoreConfig.store_name}")
        store_conf: Config = settings.CONFIG
        ws_url = f"{store_conf.terminal.TERMINAL_WEBSOCKET_URL}/register_store"
        push_store_conf = {
            "name": StoreConfig.store_name,
            "address": "donknabberello:8000/donknabberello",
            "docker_container": "donknabberello",
            "terminal_button": "A",
        }

        # Start the persistent WebSocket connection
        self.websocket = PersistentWebSocket(ws_url, push_store_conf)
        loop = asyncio.get_event_loop()
        loop.create_task(self.websocket.connect_and_listen())
        loop.run_forever()

    def shutdown(self):
        """
        Clean up on Django server shutdown.
        """
        if hasattr(self, 'websocket'):
            self.websocket.stop()
