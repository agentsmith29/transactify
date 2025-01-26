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

    def __init__(self, config_file: str, disable_logs=False):
        self.logger = self._init_logger(disable_logs)
        self._str_repr = ""
        self.config_file = pathlib.Path(config_file)
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file {self.config_file} not found. Looked for {self.config_file.absolute()}")
        self.env = self._load_environment()
        #self._load_config()
        self._str_repr = ""

    def _init_logger(self, disable_logs, level=logging.INFO, ) -> logging.Logger:
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

        if disable_logs:
            root_logger.setLevel(logging.CRITICAL)
            logger.setLevel(logging.CRITICAL)
            root_logger.disabled = True
            logger.disabled = True

        return logger

    def _load_environment(self, key="ENV") -> Dict[str, str]:
        self.logger.info(f"Loading environment variables from {self.config_file}")
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

  
    
    def get_variable(self, var_path: str) -> Optional[Any]:
        keys = var_path.split(".")
        data = self.config_data['content']
        try:
            for key in keys:
                data = data[key]
            return data
        except KeyError:
            self.logger.error(f"Variable '{var_path}' not found in configuration.")
            return None

    def __str__(self) -> str:
        return f"\n{self._str_repr}"
    
    def set_all_env_vars(self):
        print("Setting all environment variables")
        # iterate through all BaseConfigField instances and set their variables as environment variables
        for member_key, member_val in self.__dict__.items():
            if isinstance(member_val, BaseConfigField):
                print(f"Setting environment variables for {member_key}")
                # iterate through all variables in the BaseConfigField instance
                for var_key, var_val in member_val.__dict__.items():
                    if var_key.startswith("_"):
                        continue
                    os.environ[var_key] = str(var_val)
                    print(f"Set {var_key}={var_val}")
        
    @staticmethod
    def from_command_line(config: BaseConfigField):
        """
        Parse command-line arguments and retrieve configuration values.
        Usage: python Config.py <config_file> --getvar "key"
        """
        import argparse

        # disaple all loggins and outputs
        logging.basicConfig(level=logging.CRITICAL)

        parser = argparse.ArgumentParser(description="ConfigParser Command Line Utility")
        parser.add_argument("config_file", type=str, help="Path to the configuration file.")
        parser.add_argument("-g", "--getvar", type=str, help="Dot-separated key to fetch from the configuration.")
        parser.add_argument("-e", "--env_setall", action='store_true', help="Set all variables as environment variables from the given file.")

        args = parser.parse_args()

        config_file = args.config_file
        key_getvar = args.getvar
        env_setall = args.env_setall

        if not config_file:
            raise ValueError("Configuration file path is required.")

        _config: ConfigParser = config(config_file, disable_logs=True)

        if key_getvar:
            keys = key_getvar.split(".")
            value = _config
            for k in keys:
                value = getattr(value, k, None)
            return value
        
        if env_setall:
            _config.set_all_env_vars()

        return None
