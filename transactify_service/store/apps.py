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
            from store.mock_store_content import (mock_store_customers, mock_store_products, 
                                                  mock_restocks, mock_customer_deposits, mock_purchases)

            logger = store.StoreLogsDBHandler.setup_custom_logging('apps')
            try:
                mock_store_customers()
                mock_customer_deposits()

                mock_store_products()
                mock_restocks()
                
                mock_purchases()
            except Exception as e:
                logger.error(f"Failed to mock store content: {e}")
            # set the name of the store
            
