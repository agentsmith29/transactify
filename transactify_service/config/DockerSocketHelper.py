
import requests
from requests_unixsocket import Session
import logging
from typing import Optional, Dict, Any
import traceback

class DockerSocketHelper():
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.socket_url = f"http+unix://%2Frun%2Fdocker.sock"
        self.session = Session()

    @property
    def socket_info(self) -> Optional[str]:
        return self._get_socket_info()
    
    def container_name(self, hostname: str) -> Optional[str]:
        _name = self._get_container_info(hostname, "Name")
        return None if _name is None else _name.lstrip("/")
    
    def container_id(self, hostname: str) -> Optional[str]:
        return self._get_container_info(hostname, "Id")

    # =================================================================================================================
    # Docker compose service methods
    # =================================================================================================================
    def _get_running_containers(self, url="containers/json"):
        """
            Get the container names associated with a Docker Compose service in a non-Swarm environment.
            
            :param service_name: The name of the service in the docker-compose file.
            :return: A list of container names, or None if the service is not found or an error occurs.
        """
        try:
            # Fetch all running containers
            containers_url = f"{self.socket_url}/{url}"
            self.logger.debug(f"Fetching running containers from {containers_url}")
            response = self.session.get(containers_url)
            response.raise_for_status()

            containers = response.json()
            # for idx, container in enumerate(containers):
            #     print(f"Container JSON ({idx}/{len(containers)}): {container}")
            self.logger.debug(f"Found {len(containers)} running containers")
            if containers:
                return containers
            else:
                self.logger.warning(f"No containers found or no running containers")
                return None
        except Exception as e:
            self.logger.error(f"Unexpected error when fetching running containers: {e}")
            return None

    def _container_info_from_service(self, service_name: str, key: str, allow_multiple=False) -> Optional[str]:
        """
        Get the container names associated with a Docker Compose service in a non-Swarm environment.
        
        :param service_name: The name of the service in the docker-compose file.
        :return: A list of container names, or None if the service is not found or an error occurs.
        """
        try:
            containers = self._get_running_containers()
            container_info = []

            for container in containers:
                # Check if the service name matches the docker-compose service label
                labels = container.get("Labels", {})
                if labels.get("com.docker.compose.service") == service_name:
                    self.logger.debug(f"Found container for service {service_name}.")
                    container_key = container.get(key, [None])
                    self.logger.debug(f"Extracting key <{key}> from container info: {container_key} (type: {type(container_key)})")
                    if container_key:
                        container_info.append(container_key)
                    else:
                        self.logger.warning(f"container_info was empty")

            if not allow_multiple:
                if len(container_info) > 1:
                    raise ValueError(f"Multiple containers found for service {service_name}. Only one container is expected." 
                                 f"Please ensure that only one container with '{service_name}' is running for the service.")
                container_info =  container_info[0]
            
            if container_info and len(container_info) > 0:
                self.logger.debug(f"Found container info: {container_info} (len: {len(container_info)})")
                return container_info
            else:
                self.logger.warning(f"No containers found for service {service_name}")
                return None
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return None

    def container_name_from_service(self, service_name: str, key: str="Names") -> Optional[str]:
        """
        Get the container names associated with a Docker Compose service in a non-Swarm environment.
        
        :param service_name: The name of the service in the docker-compose file.
        :return: A list of container names, or None if the service is not found or an error occurs.
        """
        try:
            self.logger.info(f"Fetching container name for service {service_name} from docker socket")
            container_name = self._container_info_from_service(service_name, key)
            if container_name and len(container_name) > 0:
                container_name = container_name[0].strip("/")
                self.logger.info(f"Container name: {container_name} for service {service_name}")
                return container_name
            else:
                self.logger.warning(f"No containers found for service {service_name}")
                return None
            
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return None
    
    def container_id_from_service(self, service_name: str, key: str="Id") :
        """
        Get the container names associated with a Docker Compose service in a non-Swarm environment.
        
        :param service_name: The name of the service in the docker-compose file.
        :return: A list of container names, or None if the service is not found or an error occurs.
        """
        try:
            self.logger.info(f"Fetching container ID for service {service_name} from docker socket")
            container_id = self._container_info_from_service(service_name, key)
            if container_id:
                self.logger.info(f"Container ID {container_id} for service {service_name}")
                return container_id
            else:
                self.logger.warning(f"No containers found for service {service_name}")
                return None
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return None


    # =================================================================================================================
    # Docker methods via hostname
    # =================================================================================================================
    def _get_container_data(self, hostname):
        try:
            docker_socket_url = f"{self.socket_url}/containers/{hostname}/json"
            response = self.session .get(docker_socket_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                self.logger.warning(f"Container {hostname} not found. Are your running on the host machine?")
                return None
            else:
                self.logger.error(f"Error retrieving container data: {e}")
        except Exception as e:
            self.logger.error(f"Error retrieving container data: {e}")  #<non>: Improved exception handling
            traceback.print_exc()
            return None
        
    def _get_container_info(self, hostname, key) -> Optional[str]:
            try:
                container_info = self._get_container_data(hostname)
                if container_info:
                    container_info = container_info.get(key, "")
                    self.logger.info(f"Extracting key <{key}> from container info: {container_info} (type: {type(container_info)})")
                return container_info
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    self.logger.warning(f"Container {hostname} not found. Are your running on the host machine?")
                    return None
                else:
                    self.logger.error(f"Error retrieving container data: {e}")
            except Exception as e:
                self.logger.error(f"Error retrieving container data: {e}")  #<non>: Improved exception handling
                traceback.print_exc()
                return None

    def _get_socket_info(self) -> Optional[str]:
            try:
                docker_socket_url = f"{self.socket_url}/info"
                r = self.session.get(docker_socket_url)
                socket_info = r.json()
                return socket_info
            except Exception as e:
                self.logger.error(f"Error retrieving socket info: {e}")  #<non>: Improved exception handling
                return None

