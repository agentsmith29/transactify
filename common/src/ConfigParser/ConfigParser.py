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
from .capture_assigned_var import capture_assigned_var

import os


class FinalizeMeta(type):
    def __new__(cls, name, bases, class_dict):
        # Get the original __init__ (if any) from the class dictionary
        original_init = class_dict.get('__init__')

        # Define a new __init__ that wraps the original one
        def new_init(self, *args, **kwargs):
            # Call the original __init__ if it exists
            if original_init:
                original_init(self, *args, **kwargs)
            # Call self.finalize() after initialization
            self._finalize()

        # Replace the __init__ in the class dictionary with the new one
        class_dict['__init__'] = new_init
        return super().__new__(cls, name, bases, class_dict)


class ConfigParser(metaclass=FinalizeMeta):

    def __init__(self, config_file: str):
        self.logger = self._init_logger()
        self._str_repr = ""
        self.config_file = pathlib.Path(config_file)
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file {self.config_file} not found.")
        self.env = self._load_environment()
        #self._load_config()
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

    def _finalize(self):
        
        for member_key, member_val in self.__dict__.items():
            if isinstance(member_val, BaseConfigField):
                # call the replace_keywords method to replace placeholders in the config
                member_val.replace_keywords()
                self._str_repr += f"{member_val}\n"
        self.logger.info(f"Configuration loaded successfully.")
        self.logger.info(f"{self}")
    
    @capture_assigned_var(arg_name='var_name')
    def load(self, cfg: BaseConfigField, var_name, **kwargs) -> BaseConfigField:
        _kwargs = {"data": self.config_data, "logger": self.logger}    
        _kwargs = {**_kwargs, **kwargs}
        return cfg(**_kwargs)

    def __str__(self) -> str:
        return f"\n{self._str_repr}"
