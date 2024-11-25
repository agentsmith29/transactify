from django.db import models
from .Store import Store

class StoreProduct(models.Model):
    """Represents a product bound to a specific store."""
    id = models.AutoField(primary_key=True)
    ean = models.CharField(max_length=13, unique=True)  # EAN code
    name = models.CharField(max_length=100)
    stock_quantity = models.PositiveIntegerField(default=0)
    resell_price = models.DecimalField(max_digits=10, decimal_places=2)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")

    def __str__(self):
        return f"{self.name} ({self.store.name})"


