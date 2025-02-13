import sys
import os
from config.Config import Config
import transactify_service.is_running_migrations as is_running_migrations

        
def load_config(CONF_FILE):
    try:
        if not CONF_FILE:
            raise ValueError("Error: CONFIG_FILE environment variable is not set ")
        # Check if the CONFIG_FILE exists
        if not os.path.exists(CONF_FILE):
            raise ValueError("Error: CONFIG_FILE file does not exist.")
        return Config(CONF_FILE, disable_logs=True)
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)
# Initialize the ConfigParser with the YAML file path
CONF_FILE = os.getenv("CONFIG_FILE")
CONFIG = load_config(CONF_FILE)