import yaml
import os
import pathlib
import socket
import requests

class ConfigParser:
    class DatabaseConfig:
        def __init__(self, data, env):
            self.DB_RESET = self._replace_with_env(data.get("DB_RESET", "false"), env)
            self.REMIGRATE = self._replace_with_env(data.get("REMIGRATE", "false"), env)
            self.DJANGO_DB_HOST = self._replace_with_env(data.get("DJANGO_DB_HOST", "db"), env)
            self.DJANGO_DB_PORT = self._replace_with_env(data.get("DJANGO_DB_PORT", "${DB_PORT}"), env)
            self.DJANGO_DB_USER = self._replace_with_env(data.get("DJANGO_DB_USER", "${DB_USER}"), env)
            self.DJANGO_DB_PASSWORD = self._replace_with_env(data.get("DJANGO_DB_PASSWORD", "${DB_PASSWORD}"), env)

        def _replace_with_env(self, value, env):
            if value.startswith("${") and value.endswith("}"):
                return env.get(value[2:-1], f"{value[2:-1]}_NOT_SET")
            return value

    class WebConfig:
        def __init__(self, data, env):
            self.SERVICE_NAME = self._replace_with_env(data.get("SERVICE_NAME", "default_service"), env)
            self.DJANGO_WEB_PORT = self._replace_with_env(data.get("DJANGO_WEB_PORT", "${PROJECT_PORT}"), env)
            self.DJANGO_WEB_HOST = self._replace_with_env(data.get("DJANGO_WEB_HOST", "${PROJECT_HOST}"), env)

        def _replace_with_env(self, value, env):
            if value.startswith("${") and value.endswith("}"):
                return env.get(value[2:-1], f"{value[2:-1]}_NOT_SET")
            return value

    class AdminConfig:
        def __init__(self, data):
            self.ADMIN_USER = data.get("ADMIN_USER", "admin")
            self.ADMIN_PASSWORD = data.get("ADMIN_PASSWORD", "admin")
            self.ADMIN_EMAIL = data.get("ADMIN_EMAIL", "admin@admin.com")

    class TerminalConfig:
        def __init__(self, data, env):
            self.TERMINAL_SERVICES = self._replace_with_env(data.get("TERMINAL_SERVICES", "http://localhost:8000/terminal"), env)

        def _replace_with_env(self, value, env):
            if value.startswith("${") and value.endswith("}"):
                return env.get(value[2:-1], f"{value[2:-1]}_NOT_SET")
            return value

    class ContainerConfig:
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

        self.database = self.DatabaseConfig(config_data.get("database", {}), self.env)
        self.webconfig = self.WebConfig(config_data.get("webconfig", {}), self.env)
        self.admin = self.AdminConfig(config_data.get("admin", {}))
        self.terminal = self.TerminalConfig(config_data.get("terminal", {}), self.env)
        self.container = self.ContainerConfig()


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
