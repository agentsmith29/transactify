from django.apps import AppConfig
import os
import logging
from config.Config import Config
from django.conf import settings
import asyncio
import websockets
import json
from .websocket import PersistentWebSocket
from django.db import connection
from django.apps import apps
import sys

def is_running_migration():
    """
    Check if a migration is being executed.
    """
    migrate_keywords = ['migrate', 'makemigrations', 'createsuperuser', 'create_or_update_superuser',
                        'collectstatic']
    # Check if 'migrate' or 'makemigrations' is in the command-line arguments
    for keyword in migrate_keywords:
        if keyword in sys.argv:
            return True
    
    # Optionally check the queries log for "migrate" commands
    for query in connection.queries_log:
        if 'migrate' in query.get('sql', ''):
            return True
    
    return False
        
class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        from transactify_service.settings import CONFIG
        
    
        if not is_running_migration():
            logger = logging.getLogger(f'{CONFIG.webservice.SERVICE_NAME}.apps')
            logger.debug(f"The application is ready and everything is setup.")
            if os.environ.get('MIGRATE_HISTORICAL', '0') == '1':
                logger.warning("Initializing mock store content... Set INIT_DATA=0 to disable.")
                from store.data_generators.add_historical_data import HistoricalData
                try:
                    HistoricalData()
                except Exception as e:
                    logger.error(f"Failed to mock store content: {e}")

            # WebSocket configuration
            ws_url = f"{CONFIG.terminal.TERMINAL_WEBSOCKET_URL}/configure"
            logger.info(f"Push configureation to terminal: {CONFIG.webservice.SERVICE_NAME} to {ws_url}")
            push_store_conf = {
                "cmd": "register_store",
                "params": {
                    "name": CONFIG.webservice.FRIENDLY_NAME,
                    "address": CONFIG.webservice.SERVICE_URL,
                    "docker_container": CONFIG.container.CONTAINER_NAME,
                    "terminal_button": CONFIG.terminal.TERMINAL_SELECTION_BUTTONS,
                }
            }
            logger.debug(f"Pushing configuration: {push_store_conf}")
            
            try:
                global websocket
                # Start the persistent WebSocket connection
                websocket = PersistentWebSocket(ws_url, push_store_conf)
                websocket.start()
                
            except Exception as e:
                logger.error(f"Failed to start persistent websocket connection: {e}.")
        else:
            logger = logging.getLogger(f'root.apps')
            logger.info("Migration is running, skipping websocket initialization.")
    
        
    def shutdown(self):
        """
        Clean up on Django server shutdown.
        """
        if hasattr(self, 'websocket'):
            self.websocket.stop()
