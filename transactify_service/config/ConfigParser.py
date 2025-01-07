import yaml
import os
import pathlib
import socket
import requests

class BaseConfigField():
    def __init__(self, data, env, field_name):
        self.field_name = field_name
        self._data = {}
        # flatten the data
        for key, value in data.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    self._data[k] = v

        self._data_field = data.get(field_name, {})
        self._env = env
        

    def _replace_with_env(self, value):
            
            
            return value

    def _replace_inconfig(self, value):
            # all values in the config file are also variables
            
            for key, data_val in self._data.items():
                if "${"+key+"}" in value:
                    value = value.replace("${"+key+"}", data_val)
                    print(f"{value} -> ", end="")   
            
            for env_key, env_value in self._env.items():
                if "${ENV."+env_key+"}" in value:
                    value =  value.replace("${ENV."+env_key+"}", env_value)
                    print(f"{value} -> ", end="")   
            
            if "${" in value and "}" in value:
                value = self._replace_with_env(value)

            return value
    
    def assign(self, key, default=None, required=True):
        if required and default is not None:
            required = False
        else:
            required = True

        if default is None:
            required = True
        elif default.strip() != "":
            required = False


        try:
            _value = self._data_field.get(key, default)
            # split the values between 
        except Exception as e:
            _value = default
            raise e
        _val = _value
        print(f"Key: {key}, Value: {_value} -> ", end="")   
        _val = self._replace_inconfig(_val)
        print(f"{_val}")   
         
        if required and _val is None or _val == f"_{key}_NOT_SET" or _val == "":
            raise ValueError(f"Required field {key} not set.")
        return _val

    def __str__(self):
        ret_dict = self.__dict__
        # remove private variables
        for key in list(ret_dict.keys()):
            if key.startswith("_"):
                del ret_dict[key]
        return str(ret_dict)

class ConfigParser:
    class DatabaseConfig(BaseConfigField):
        def __init__(self, data, env):
            super().__init__(data, env, "database")
            self.DB_RESET = self.assign("DB_RESET", "false")
            self.REMIGRATE = self.assign("REMIGRATE", "false")
            
            self.NAME = self.assign("DB_NAME")
            self.HOST = self.assign("DB_HOST")
            self.PORT = self.assign("DB_PORT")
            self.USER = self.assign("DB_USER")
            self.PASSWORD = self.assign("DB_PASSWORD")


    class WebService(BaseConfigField):
        def __init__(self, data, env):
            super().__init__(data, env, "webservice")
            self.SERVICE_NAME = self.assign("SERVICE_NAME")
            self.SERVICE_WEB_PORT = self.assign("SERVICE_WEB_PORT")
            self.SERVICE_WEB_HOST = self.assign("SERVICE_WEB_HOST")


    class AdminConfig(BaseConfigField):
        def __init__(self, data, env):
            super().__init__(data, env, "admin")
            self.ADMIN_USER = self.assign("ADMIN_USER", "admin")
            self.ADMIN_PASSWORD = self.assign("ADMIN_PASSWORD", "admin")
            self.ADMIN_EMAIL = self.assign("ADMIN_EMAIL", "admin@admin.com")

    class TerminalConfig(BaseConfigField):

        def __init__(self, data, env):
            super().__init__(data, env, "terminal")
            self.TERMINAL_SERVICES = self.assign("TERMINAL_SERVICES")


    class ContainerConfig(BaseConfigField):
        def __init__(self):
            self.HOSTNAME = self._get_hostname()
            self.CONTAINER_NAME = self._get_container_name()

        def _get_hostname(self):
            """
            Get the hostname of the current system.
            """
            return socket.gethostname()

        def _get_container_name(self):
            """
            Get the Docker container name using the Docker socket API.
            """
            try:
                # Docker socket path
                docker_socket_url = f"http://docker/containers/{self.HOSTNAME}/json"
                headers = {"Content-Type": "application/json"}
                
                # Use Docker's Unix socket
                response = requests.get(docker_socket_url, headers=headers, 
                                        timeout=5, 
                                        unix_socket="/run/docker.sock")
                response.raise_for_status()

                # Parse the container name from the response
                container_data = response.json()
                container_name = container_data.get("Name", "").lstrip("/")
                return container_name
            except Exception as e:
                print(f"Error retrieving container name: {e}")
                return None

    def __init__(self, config_file):
        self.config_file = pathlib.Path(config_file)
        # Check if the file exists
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file {self.config_file} not found.")
        self.env = self._load_environment()
        self._load_config()

    def _load_environment(self):
        """
        Load the environment variables from the .env file specified in the YAML config.
        """
        with open(self.config_file, 'r') as file:
            config_data = yaml.safe_load(file)
            env_file_path = pathlib.Path(self.config_file.parent / config_data.get("environment")).resolve()
            print(f"Loading environment variables from {env_file_path}")

            env = {}
            if env_file_path and env_file_path.exists():
                with open(str(env_file_path), 'r') as env_file:
                    for line in env_file:
                        line = line.strip()
                        try:
                            if line and not line.startswith("#") and "=" in line:
                                key, value = line.split("=", 1)
                                env[key.strip()] = value.strip()
                        except Exception as e:
                            print(f"Error reading line: {line}")
                            print(e)
            return env

    def _load_config(self):
        """
        Load the YAML configuration file and initialize sections.
        """
        with open(self.config_file, 'r') as file:
            config_data = yaml.safe_load(file)

        self.database = self.DatabaseConfig(config_data, self.env)
        self.webservice = self.WebService(config_data, self.env)
        self.admin = self.AdminConfig(config_data, self.env)
        self.terminal = self.TerminalConfig(config_data, self.env)
        self.container = self.ContainerConfig()

    def __str__(self):
        return f"databse:\n {self.database}\nwebservice:\n {self.webservice}\nadmin:\n {self.admin}\nterminal:\n {self.terminal}\ncontainer:\n {self.container}"
    
# Example usage
if __name__ == "__main__":
    config = ConfigParser("config.yaml")

    print("Database Configuration:")
    print(f"DB_RESET: {config.database.DB_RESET}")
    print(f"Django DB Host: {config.database.DJANGO_DB_HOST}")

    print("\nWeb Configuration:")
    print(f"Service Name: {config.webconfig.SERVICE_NAME}")
    print(f"Web Host: {config.webconfig.DJANGO_WEB_HOST}")

    print("\nAdmin Configuration:")
    print(f"Admin User: {config.admin.ADMIN_USER}")

    print("\nTerminal Configuration:")
    print(f"Terminal Services: {config.terminal.TERMINAL_SERVICES}")
