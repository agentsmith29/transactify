import sys
import os

# config/__init__.py
from .Config import Config

# Initialize the ConfigParser with the YAML file path
CONFIG = Config("./configs/store_config.yaml")
