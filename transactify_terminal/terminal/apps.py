from django.apps import AppConfig
import logging
import os
import traceback

class TerminalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'terminal'

    def ready(self):
        logger = logging.getLogger('hwc')  # Create a new logger
        # get the current ip and port of django server
        try:

            from .controller.HardwareController import HardwareController
            global hwcontroller
            hwcontroller = HardwareController()
        except Exception as e:
            logger.error(f"Failed to initialize hardware controller: {e}")
            traceback.print_exc()
            os._exit(1)
