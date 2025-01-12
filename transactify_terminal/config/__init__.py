import sys
import os
# get current file path
_filepwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{_filepwd}/../../common/src')

from .Config import Config

# Initialize the ConfigParser with the YAML file path
CONFIG = Config("./configs/terminal_config.yaml")
