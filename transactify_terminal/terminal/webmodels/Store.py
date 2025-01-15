from django.db import models


class Store(models.Model):
    service_name = models.CharField(max_length=255, unique=True)  # Internal service name
    name = models.CharField(max_length=255, null=True, blank=True)  # Store's name
    web_address = models.URLField(null=True, blank=True)  # Web service URL for the store
    docker_container = models.CharField(max_length=255, null=True, blank=True)  # Docker container name
    terminal_button = models.CharField(max_length=5, null=True, blank=True)  # Terminal button identifier
    is_connected = models.BooleanField(default=False)  # Connection status

    def __str__(self):
        return self.name or f"Store {self.uid}"
