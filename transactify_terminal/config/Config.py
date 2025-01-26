import socket
import sys
import os
# get current file path
_filepwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{_filepwd}/../../common/src')

from ConfigParser.ConfigParser import ConfigParser
from ConfigParser.BaseConfigFields import BaseConfigField
from ConfigParser.DockerSocketHelper import DockerSocketHelper


import os

class DatabaseConfig(BaseConfigField):
    def __init__(self, *args, **kwargs):
        super().__init__(field_name="database", *args, **kwargs)
        self.RESET = self.assign_from_config("RESET", "false")
        self.REMIGRATE = self.assign_from_config("REMIGRATE", "false")
        self.NAME = self.assign_from_config("NAME")
        self.HOST = self.assign_from_config("HOST")
        self.PORT = self.assign_from_config("PORT")
        self.USER = self.assign_from_config("USER")
        self.PASSWORD = self.assign_from_config("PASSWORD")

class WebService(BaseConfigField):
    def __init__(self, *args, **kwargs):
        super().__init__(field_name="webservice", *args, **kwargs)
        self.SERVICE_NAME = self.assign_from_config("SERVICE_NAME")
        self.SERVICE_WEB_PORT = self.assign_from_config("SERVICE_WEB_PORT")
        self.SERVICE_WEB_HOST = self.assign_from_config("SERVICE_WEB_HOST")

class AdminConfig(BaseConfigField):
    def __init__(self, *args, **kwargs):
        super().__init__(field_name="admin", *args, **kwargs)
        self.ADMIN_USER = self.assign_from_config("ADMIN_USER", "admin")
        self.ADMIN_PASSWORD = self.assign_from_config("ADMIN_PASSWORD", "admin")
        self.ADMIN_EMAIL = self.assign_from_config("ADMIN_EMAIL", "admin@admin.com")

class ContainerConfig(BaseConfigField):
    def __init__(self, *args, **kwargs):
        super().__init__(field_name="container", *args, **kwargs)
        self.docker_socket_helper = DockerSocketHelper(self.logger)
        self.HOSTNAME = self.assign_direct(self._get_hostname())
        self.CONTAINER_NAME = self.assign_direct(self.docker_socket_helper.container_name(f"{self.HOSTNAME}"))
        self.CONTAINER_ID = self.assign_direct(self.docker_socket_helper.container_id(f"{self.HOSTNAME}"))

    def _get_hostname(self) -> str:
        hostname = socket.gethostname()
        return hostname

class DjangoConfig(BaseConfigField):
    def __init__(self, data, field_name, logger):
        super().__init__(data, field_name, logger)
        self.DEBUG = bool(self.assign_from_config("DJANGO_DEBUG", "False"))
        self.SECRET_KEY = str(self.assign_from_config("SECRET_KEY", "Secret"))
        self.STATIC_ROOT = str(self.assign_direct(os.getenv("DIR_STATIC", "/app/static/")))
        # Handeling static files

        self.STATIC_URL = str(self.assign_from_config("STATIC_URL", "static/"))
        self.STATIC_ASSETS_PATH = str(self.assign_from_config("STATIC_ASSETS_PATH", "assets/"))
        self.STATIC_WEBSERVER = str(self.assign_from_config("STATIC_WEBSERVER", None, required=False,
                                                            lambda_apply_func=lambda url: self.wrap_url(url, f"http")))

class OLEDConfig(BaseConfigField):
    def __init__(self, *args, **kwargs):
        super().__init__(field_name="oled", *args, **kwargs)
        self.OLED_WIDTH = self.assign_from_config("OLED_WIDTH", "256")
        self.OLED_HEIGHT = self.assign_from_config("OLED_HEIGHT", "64")
        self.OLED_RESET_PIN = self.assign_from_config("OLED_RESET_PIN", "24")
        self.OLED_DC_PIN = self.assign_from_config("OLED_DC_PIN", "23")
        self.OLED_SPI_PORT = self.assign_from_config("OLED_SPI_PORT", "0")
        self.OLED_SPI_DEVICE = self.assign_from_config("OLED_SPI_DEVICE", "0")
  
class KeyPadConfig(BaseConfigField):
    def __init__(self, *args, **kwargs):
        super().__init__(field_name="keypad", *args, **kwargs)
        self.KEYPAD_ROWS = self.assign_from_config("KEYPAD_ROWS", [26, 19, 13, 6])
        self.KEYPAD_COLS = self.assign_from_config("KEYPAD_COLS", [5, 16, 20, 21])

class LEDConfig(BaseConfigField):
    def __init__(self, *args, **kwargs):
        super().__init__(field_name="ledstrip", *args, **kwargs)
        self.LED_COUNT = self.assign_from_config("LED_COUNT", 8)
        self.LED_PIN = self.assign_from_config("LED_PIN", 18)
        self.LED_FREQ_HZ = self.assign_from_config("LED_FREQ_HZ", 800000)
        self.LED_DMA = self.assign_from_config("LED_DMA", 10)
        self.LED_BRIGHTNESS = self.assign_from_config("LED_BRIGHTNESS", 255)
        self.LED_INVERT = self.assign_from_config("LED_INVERT", False)
        self.LED_CHANNEL = self.assign_from_config("LED_CHANNEL", 0)

class BarCodeReaderConfig(BaseConfigField):
    def __init__(self, *args, **kwargs):
        super().__init__(field_name="barcode_reader", *args, **kwargs)
        self.DEVICE_PATH = self.assign_from_config("DEVICE_PATH", "/dev/ttyACM0")
        self.BAUDRATE = self.assign_from_config("BAUDRATE", 115200)
        self.BYTESIZE = self.assign_from_config("BYTESIZE", 8)
        self.PARITY = self.assign_from_config("PARITY", "N")
        self.STOPBITS = self.assign_from_config("STOPBITS", 1)
        self.TIMEOUT = self.assign_from_config("TIMEOUT", 1)


class Config(ConfigParser):

    def __init__(self, config_file: str, *args, **kwargs):
        super().__init__(config_file, *args, **kwargs)

        self.database: DatabaseConfig = self.load(DatabaseConfig)
        self.webservice: WebService= self.load(WebService)
        self.admin: AdminConfig = self.load(AdminConfig)
        self.container: ContainerConfig = self.load(ContainerConfig)
        self.django: DjangoConfig = self.load(DjangoConfig, field_name="django")
        self.oled: OLEDConfig = self.load(OLEDConfig)
        self.keypad: KeyPadConfig = self.load(KeyPadConfig)
        self.ledstrip: LEDConfig = self.load(LEDConfig)
        self.barcode_reader: BarCodeReaderConfig = self.load(BarCodeReaderConfig)

if __name__ == "__main__":
    print(Config.from_command_line(Config))