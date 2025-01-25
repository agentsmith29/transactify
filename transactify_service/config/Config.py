import socket
import sys
import os

_filepwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{_filepwd}/../../common/src')

from ConfigParser.ConfigParser import ConfigParser
from ConfigParser.BaseConfigFields import BaseConfigField
from ConfigParser.DockerSocketHelper import DockerSocketHelper

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
        self.SERVICE_URL = self.assign_direct(f"http://{self.SERVICE_WEB_HOST}:{self.SERVICE_WEB_PORT}/{self.SERVICE_NAME}")
        self.JOURNAL_FILE = self.assign_from_config("JOURNAL_FILE", f"./journal_{self.SERVICE_NAME}.py")

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
        self.TERMINAL_SELECTION_BUTTONS = self.assign_from_config("TERMINAL_SELECTION_BUTTONS", "A")

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

class Config(ConfigParser):
    def __init__(self, config_file: str, *args, **kwargs):
        super().__init__(config_file, *args, **kwargs)

        self.database: DatabaseConfig = self.load(DatabaseConfig)
        self.webservice: WebService = self.load(WebService)
        self.admin: AdminConfig = self.load(AdminConfig)
        self.terminal: TerminalConfig = self.load(TerminalConfig)
        self.container: ContainerConfig = self.load(ContainerConfig)
        self.django: DjangoConfig = self.load(DjangoConfig, field_name="django")  


if __name__ == "__main__":
    print(Config.from_command_line(Config))