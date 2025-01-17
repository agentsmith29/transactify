"""Database Model that should represent the cash in the store"""

from django.db import models
from django.utils import timezone

class StoreCash(models.Model):
    """Database Model that should represent the cash in the store"""
    cash = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Store Cash: {self.cash}"