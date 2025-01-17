from django.apps import AppConfig
import os
import logging
from config.Config import Config
from django.conf import settings
import asyncio
import websockets
import json
from .websocket import PersistentWebSocket


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
                    print(f"Failed to mock store content: {e}")

        # WebSocket configuration
        print(f"Push store name to terminal: {StoreConfig.store_name}")
        store_conf: Config = settings.CONFIG
        ws_url = f"{store_conf.terminal.TERMINAL_WEBSOCKET_URL}/register_store"
        push_store_conf = {
            "name": store_conf.webservice.SERVICE_NAME,
            "address": store_conf.webservice.SERVICE_URL,
            "docker_container": store_conf.container.CONTAINER_NAME,
            "terminal_button": store_conf.terminal.TERMINAL_SELECTION_BUTTONS,
        }

        # Start the persistent WebSocket connection
        self.websocket = PersistentWebSocket(ws_url, push_store_conf)
        self.websocket.start()

    def shutdown(self):
        """
        Clean up on Django server shutdown.
        """
        if hasattr(self, 'websocket'):
            self.websocket.stop()
