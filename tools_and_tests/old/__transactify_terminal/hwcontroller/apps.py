from django.apps import AppConfig
import logging
import os

hwcontroller = None

class HwcontrollerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hwcontroller'

    def ready(self):
        logger = logging.getLogger('hwc')  # Create a new logger
        # get the current ip and port of django server
        #try:
        from .controller.HardwareController import HardwareController
        global hwcontroller
        hwcontroller = HardwareController()
        #except Exception as e:
        #logger.error(f"Error initializing HardwareController: {e}")
