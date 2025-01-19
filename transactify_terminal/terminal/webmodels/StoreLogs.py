from django.db import models
from .LogTraceback import LogTraceback

class StoreLog(models.Model):
    loglevel = models.CharField(max_length=50)
    module = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    traceback = models.ForeignKey(LogTraceback, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"[{self.loglevel}] {self.module}: {self.message}"
