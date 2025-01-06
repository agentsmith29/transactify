from django.apps import AppConfig
import os
import logging
hwcontroller = None

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        # setup the logger
        import store.StoreLogsDBHandler	  # Import your custom logging here
        logger = store.StoreLogsDBHandler.setup_custom_logging('apps')
       
        # set the name of the store
        self.store_name = os.getenv('SERVICE_NAME')
