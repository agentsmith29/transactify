from django.db import models
from .Store import Store

class StoreConnection(models.Model):
    uid = models.CharField(max_length=36, unique=True)  # UUID for the WebSocket connection
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="connections", null=True, blank=True)  # Associated store
    connected_at = models.DateTimeField(auto_now_add=True)  # Timestamp when connection was established
    disconnected_at = models.DateTimeField(null=True, blank=True)  # Timestamp when connection was closed
    is_active = models.BooleanField(default=True)  # Connection state
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Client IP address
    port = models.PositiveIntegerField(null=True, blank=True)  # Client port

    def __str__(self):
        return f"Connection {self.uid} ({'Active' if self.is_active else 'Inactive'})"
