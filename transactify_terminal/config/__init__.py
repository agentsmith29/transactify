import sys
import os
from config.Config import Config

# Initialize the ConfigParser with the YAML file path
CONF_FILE = os.getenv("CONFIG_FILE")
try:
    if not CONF_FILE:
        raise ValueError("Error: CONFIG_FILE environment variable is not set.")
    CONFIG = Config(CONF_FILE, disable_logs=True)
except FileNotFoundError as e:
    print(e)
    sys.exit(1)
