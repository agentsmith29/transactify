from django.db import models

class Store(models.Model):
    """Represents an individual store."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


