from django.apps import AppConfig
import os
import logging
from config.Config import Config
from django.conf import settings
import asyncio
import websockets
import json

def push_store_config_to_terminal():
    # Store configuration data
    push_store_conf = {
        "name": "Don Knabberello",
        "address": "donknabberello:8000/donknabberello",
        "docker_container": "donknabberello",
        "terminal_button": "A"
    }
    store_conf: Config  = settings.CONFIG
    # WebSocket URL for the terminal
    ws_url = f"{store_conf.terminal.TERMINAL_WEBSOCKET_URL}/register_store"

    async def push_store_config():
        try:
            print(f"Connecting to terminal at: {ws_url}")
            # Connect to the terminal WebSocket server
            async with websockets.connect(ws_url) as websocket:
                # Send the store configuration as JSON
                await websocket.send(json.dumps(push_store_conf))
                print(f"Sent store config to terminal: {push_store_conf}")

                # Wait for a response
                response = await websocket.recv()
                print(f"Response from terminal: {response}")

        except Exception as e:
            print(f"Error communicating with terminal: {e}")

    # Run the asyncio event loop
    asyncio.get_event_loop().run_until_complete(push_store_config())

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        # setup the logger
        StoreConfig.store_name = os.getenv('SERVICE_NAME')

        if os.environ.get('RUN_SERVER', 'false') == 'true':
            import store.StoreLogsDBHandler	  # Import your custom logging here
            #from transactify_service.store.data_generators.mock_store_content import (mock_store_customers, mock_store_products, 
            #                                      mock_restocks, mock_customer_deposits, mock_purchases)
            from store.data_generators.add_historical_data import HistoricalData

            logger = store.StoreLogsDBHandler.setup_custom_logging('apps')

        if os.environ.get('INIT_DATA', '0') == '1':
            try:
                HistoricalData()
            except Exception as e:
                    logger.error(f"Failed to mock store content: {e}")
        
        # set the name of the store
        print(f"Push store name to terminal: {StoreConfig.store_name}")
        # post it to the terminal using the websocket
        push_store_config_to_terminal()
        

        
