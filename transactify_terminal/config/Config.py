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
        self.DB_RESET = self.assign_from_config("DB_RESET", "false")
        self.REMIGRATE = self.assign_from_config("REMIGRATE", "false")
        self.NAME = self.assign_from_config("DB_NAME")
        self.HOST = self.assign_from_config("DB_HOST")
        self.PORT = self.assign_from_config("DB_PORT")
        self.USER = self.assign_from_config("DB_USER")
        self.PASSWORD = self.assign_from_config("DB_PASSWORD")

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
  

class Config(ConfigParser):

    def __init__(self, config_file: str, *args, **kwargs):
        super().__init__(config_file, *args, **kwargs)

        self.database: DatabaseConfig = self.load(DatabaseConfig)
        self.webservice: WebService= self.load(WebService)
        self.admin: AdminConfig = self.load(AdminConfig)
        self.container: ContainerConfig = self.load(ContainerConfig)
        self.django: DjangoConfig = self.load(DjangoConfig, field_name="django")
        self.oled: OLEDConfig = self.load(OLEDConfig)

if __name__ == "__main__":
    print(Config.from_command_line(Config))