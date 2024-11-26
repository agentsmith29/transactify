from django.db import models
from .Store import Store

class StoreProduct(models.Model):
    """Represents a product bound to a specific store."""
    ean = models.CharField(primary_key=True, unique=True, null=False)  # EAN code
    name = models.CharField(max_length=100, default="Generic Product")
    stock_quantity = models.PositiveIntegerField(default=0)
    resell_price = models.DecimalField(max_digits=10, default = 0, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.store.name})"


