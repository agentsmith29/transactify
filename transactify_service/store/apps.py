from django.apps import AppConfig
import os
import logging

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        # setup the logger
        StoreConfig.store_name = os.getenv('SERVICE_NAME')

        if os.environ.get('RUN_SERVER', 'false') == 'true':
            import store.StoreLogsDBHandler	  # Import your custom logging here
            from store.mock_store_content import mock_store_content

            logger = store.StoreLogsDBHandler.setup_custom_logging('apps')
            mock_store_content()
            # set the name of the store
            
