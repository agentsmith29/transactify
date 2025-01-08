import yaml
import logging
from rich.logging import RichHandler

import pathlib
import socket
from requests_unixsocket import Session

from typing import Optional, Dict, Any
from functools import wraps
from typing import Optional, Any
from .BaseConfigFields import BaseConfigField
from .DockerSocketHelper import DockerSocketHelper



class ConfigParser:

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
            self.TERMINAL_SERVICES = self.assign_from_config("TERMINAL_SERVICES")
            self.TERMINAL_CONTAINER_NAME = self.assign_direct(
                self.docker_socket_helper.container_name_from_service(self.TERMINAL_SERVICES)
            )
            self.TERMINAL_CONTAINER_ID = self.assign_direct(
                self.docker_socket_helper.container_id_from_service(self.TERMINAL_SERVICES)
            )

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

    def __init__(self, config_file: str):
        self.logger = self._init_logger()
        self._str_repr = ""
        self.config_file = pathlib.Path(config_file)
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file {self.config_file} not found.")
        self.env = self._load_environment()
        self._load_config()
        self._str_repr = ""

    def _init_logger(self, level=logging.INFO) -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)  # Set the desired log level

        # Add RichHandler
        rich_handler = RichHandler()
        rich_handler.setLevel(level)
        formatter = logging.Formatter("%(message)s", datefmt="[%X]")
        rich_handler.setFormatter(formatter)
        
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.addHandler(rich_handler)

        return logger

    def _load_environment(self, key="ENV") -> Dict[str, str]:
        with open(self.config_file, 'r') as file:
            self.config_data = {'content': yaml.safe_load(file), 'keywords': {}}
            self.logger.info(f"Loading configuration from {self.config_file}")
            env_field = self.config_data['content'].get(key)
            if not env_field:
                self.logger.warning(f"No environment field ({key}) found in the config.")
                return {}
            
            env_file_path = pathlib.Path(self.config_file.parent / env_field).resolve()
            self.logger.info(f"Loading environment variables from {env_file_path}")
            self.config_data['env'] = {}

           # env = {}
            if env_file_path.exists():
                with open(str(env_file_path), 'r') as env_file:
                    for line in env_file:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            self.config_data['env'][key.strip()] = value.strip()
                        else:
                            self.logger.debug(f"Ignoring invalid line in .env: {line}")  #<non>: Handle invalid lines
            return self.config_data


    def _load_config(self):
        kwargs = {"data": self.config_data, "logger": self.logger}
        self.database = self.DatabaseConfig(**kwargs)
        self.webservice = self.WebService(**kwargs)
        self.admin = self.AdminConfig(**kwargs)
        self.terminal = self.TerminalConfig(**kwargs)
        self.container = self.ContainerConfig(**kwargs)
       
        for member_key, member_val in self.__dict__.items():
            if isinstance(member_val, BaseConfigField):
                # call the replace_keywords method to replace placeholders in the config
                member_val.replace_keywords()
                self._str_repr += f"{member_val}\n"
        self.logger.info(f"Configuration loaded successfully.")
        self.logger.info(f"{self}")


    def __str__(self) -> str:
        return f"\n{self.database}\n{self.webservice}\n{self.admin}\n{self.terminal}\n{self.container}"
