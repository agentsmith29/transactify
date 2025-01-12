from django.db import models

class Store(models.Model):
    service_name = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    web_address = models.URLField()
    docker_container = models.CharField(max_length=255)
    terminal_button = models.CharField(max_length=255)

    def __repr__(self):
        return f"Store(name='{self.name}', address='{self.address}', docker_container='{self.docker_container}')"
