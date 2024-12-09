from django.apps import AppConfig
import os

hwcontroller = None

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        print("****** Store app is ready to go! ******")
        import logging
        #import store.custom_logging  # Import your custom logging here
        #store.custom_logging.setup_custom_logging()
        logger = logging.getLogger('store')  # Create a new logger
        # set the name of the store
        self.store_name = os.getenv('SERVICE_NAME')