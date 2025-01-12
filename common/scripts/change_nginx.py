import os
import sys
sys.path.append(f'/common/src')
from ConfigParser.ConfigParser import ConfigParser
sys.path.append(f'/app/config')
from Config import Config

def replace_placeholders(file_nginx_conf, config: Config):
    """
    Replace placeholders in the given NGINX configuration file based on the provided configuration.

    Args:
        file_nginx_conf (str): Path to the NGINX configuration file.
        config (Config): Instance of Config loaded with configurations.

    Raises:
        FileNotFoundError: If the given file does not exist.
        ValueError: If required configurations are missing.
    """

    if not file_nginx_conf or not os.path.isfile(file_nginx_conf):
        raise FileNotFoundError(f"Error: {file_nginx_conf} does not exist.")

    # Extract required values from config
    service_name = config.webservice.SERVICE_NAME
    django_web_port = config.webservice.SERVICE_WEB_PORT
    hostname = config.container.HOSTNAME

    if not service_name or not django_web_port or not hostname:
        raise ValueError("Error: SERVICE_NAME, DJANGO_WEB_PORT, and HOSTNAME must be set in the configuration.")

    # Backup the original file
    backup_file = f"{file_nginx_conf}.bak"
    os.rename(file_nginx_conf, backup_file)
    
    with open(backup_file, 'r') as file:
        content = file.read()

    # Replace placeholders
    content = content.replace("<location>", service_name)
    content = content.replace("<host>", hostname)
    content = content.replace("<port>", django_web_port)

    # Write the updated content back to the file
    with open(file_nginx_conf, 'w') as file:
        file.write(content)

    print(f"Placeholders replaced successfully in {file_nginx_conf}.")

    # Optional: Print the updated content
    with open(file_nginx_conf, 'r') as file:
        print(file.read())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python replace_nginx_placeholders.py <file_nginx_conf>")
        sys.exit(1)

    file_nginx_conf = sys.argv[1]

    # Load the configuration
    config_file_path = os.getenv("TERMINAL_CONFIG_FILE")
    if not config_file_path:
        raise ValueError("Error: TERMINAL_CONFIG_FILE environment variable is not set.")

    config = Config(config_file_path)

    try:
        replace_placeholders(file_nginx_conf, config)
        # print the updated config
        with open(config_file_path, 'r') as file:
            print(file.read())
    except (FileNotFoundError, ValueError) as e:
        print(e)
        sys.exit(1)
