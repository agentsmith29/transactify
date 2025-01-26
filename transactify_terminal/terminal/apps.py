from django.apps import AppConfig
import logging
import os
import sys
import traceback
from transactify_terminal.settings import CONFIG
APP_DIR = os.getenv('APP_DIR')
sys.path.append(f'{APP_DIR}/..')
from common.src.is_running_migration import is_running_migration



class TerminalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'terminal'
    hwcontroller = None

    def ready(self):
        # import config from settings
        if is_running_migration():

            return
        
        from transactify_terminal.settings import CONFIG        
        logger = logging.getLogger(f'{CONFIG.webservice.SERVICE_NAME}.apps')
        # get the current ip and port of django server
        try:
            logger.info("Initializing hardware controller from terminal.apps")
            from .controller.HardwareController import HardwareController
            #global hwcontroller
            self.hwcontroller = HardwareController()
            # logging.getLogger('asyncio').setLevel(logging.ERROR)
            # logging.getLogger('terminal1.consumers').setLevel(logging.ERROR)
            # logging.getLogger('terminal1.PN532').setLevel(logging.ERROR)
            # logging.getLogger('terminal1.BarcodeScanner').setLevel(logging.ERROR)
            # logging.getLogger('daphne').setLevel(logging.ERROR)
        except Exception as e:
            logger.error(f"Failed to initialize hardware controller: {e}. Application exits now.")
            logger.error(traceback.format_exc())
            os._exit(1)
