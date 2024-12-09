from django.apps import AppConfig
import os

hwcontroller = None

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        print("****** Store app is ready to go! ******")
        import logging
        import store.custom_logging  # Import your custom logging here
        store.custom_logging.setup_custom_logging()
        logger = logging.getLogger('store')  # Create a new logger
        # get the current ip and port of django server
        #logger.info(f"Store app at {os.getenv('DJANGO_WEB_HOST')}:{os.getenv('DJANGO_WEB_PORT')} is starting.")

        #from .controller.HardwareController import HardwareController
        #global hwcontroller
        #hwcontroller = HardwareController()

        

    #def create_roles(self):
    #    from django.contrib.auth.models import Group
    # 
    #    roles = ['Admin', 'Owner', 'Manager', 'Customer', 'None']
    #    for role in roles:
    #        Group.objects.get_or_create(name=role)
