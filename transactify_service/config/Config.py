import socket
import sys
import os
print(sys.path)
print("os.getcwd():", os.getcwd())

from ConfigParser.ConfigParser import ConfigParser
from ConfigParser.BaseConfigFields import BaseConfigField
from ConfigParser.DockerSocketHelper import DockerSocketHelper


import os


class Config(ConfigParser):

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

    class TerminalConfig(BaseConfigField):
        def __init__(self, *args, **kwargs):
            super().__init__(field_name="terminal", *args, **kwargs)
            self.docker_socket_helper = DockerSocketHelper(self.logger)
            self.TERMINAL_SERVICE = self.assign_from_config("TERMINAL_SERVICE")
            self.TERMINAL_CONTAINER_NAME = self.assign_direct(
                self.docker_socket_helper.container_name_from_service(self.TERMINAL_SERVICE)
            )
            self.TERMINAL_CONTAINER_ID = str(self.assign_direct(
                self.docker_socket_helper.container_id_from_service(self.TERMINAL_SERVICE)
            ))

            self.TERMINAL_SERVICE_URL = self.assign_from_config("TERMINAL_SERVICE_URL", 
                                                                lambda_apply_func=lambda url: self.wrap_url(url, f"http"))
            self.TERMINAL_WEBSOCKET_URL = self.assign_from_config("TERMINAL_WEBSOCKET_URL", 
                                                                  lambda_apply_func=lambda url: self.wrap_url(url, f"ws"))

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

    def __init__(self, config_file: str):
        super().__init__(config_file)

        self.database = self.load(self.DatabaseConfig)
        self.webservice = self.load(self.WebService)
        self.admin = self.load(self.AdminConfig)
        self.terminal = self.load(self.TerminalConfig)
        self.container = self.load(self.ContainerConfig)
        self.django = self.load(self.DjangoConfig, field_name="django")