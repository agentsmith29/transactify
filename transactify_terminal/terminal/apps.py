from django.apps import AppConfig
import logging
import os
import traceback
from transactify_terminal.settings import CONFIG

class TerminalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'terminal'

    def ready(self):
        # import config from settings
        from transactify_terminal.settings import CONFIG

        logger = logging.getLogger(f'{CONFIG.webservice.SERVICE_NAME}.apps')
        # get the current ip and port of django server
        try:
            logger.info("Initializing hardware controller from terminal.apps")
            from .controller.HardwareController import HardwareController
            global hwcontroller
            hwcontroller = HardwareController()
            # logging.getLogger('asyncio').setLevel(logging.ERROR)
            # logging.getLogger('terminal1.consumers').setLevel(logging.ERROR)
            # logging.getLogger('terminal1.PN532').setLevel(logging.ERROR)
            # logging.getLogger('terminal1.BarcodeScanner').setLevel(logging.ERROR)
            # logging.getLogger('daphne').setLevel(logging.ERROR)
        except Exception as e:
            logger.error(f"Failed to initialize hardware controller: {e}. Application exits now.")
            logger.error(traceback.format_exc())
            os._exit(1)
