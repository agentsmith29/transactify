import yaml
from typing import List

class Store:
    def __init__(self, name: str, address: str, docker_container: str, terminal_button: str):
        self.name = name
        self.address = address
        self.docker_container = docker_container
        self.terminal_button = terminal_button

    def __repr__(self):
        return f"Store(name='{self.name}', address='{self.address}', docker_container='{self.docker_container}')"

def parse_services_config_from_yaml(file_path: str) -> List[Store]:
    """
    Parse the YAML service configuration file and return a list of Store objects.

    Args:
        file_path (str): The path to the YAML configuration file.

    Returns:
        List[Store]: A list of Store instances.
    """
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)

    services = [
        Store(
            name=service["name"],
            address=service["address"],
            docker_container=service["docker_container"],
            terminal_button=service["terminal_button"],
        )
        for service in data.get("services", [])
    ]
    return services

# Example Usage
if __name__ == "__main__":
    file_path = "services.yaml"
    stores = parse_services_config_from_yaml(file_path)
    for store in stores:
        print(store)
