from django.db import models
from django.contrib.auth.models import User
import uuid

class APIKey(models.Model):
    """
    Model to store API keys for authenticated access.
    """
    key = models.CharField(max_length=40, unique=True, default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"APIKey for {self.user.username}"
