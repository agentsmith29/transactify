# config/__init__.py
from .ConfigParser import ConfigParser

# Initialize the ConfigParser with the YAML file path
CONFIG = ConfigParser("./configs/store_config.yaml")
