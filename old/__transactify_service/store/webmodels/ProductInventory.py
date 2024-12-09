from django.db import models
from django.db.models import F
from decimal import Decimal
from django.utils.timezone import now
from .ProductRestock import ProductRestock


class ProductInventory(models.Model):
    """Tracks the current inventory of products for FIFO pricing."""
    restock = models.OneToOneField(ProductRestock, on_delete=models.CASCADE, related_name="inventory")
    remaining_quantity = models.PositiveIntegerField(default=0)  # Tracks remaining units in this restock

    def __str__(self):
        return f"{self.remaining_quantity} units from restock on {self.restock.restock_date}"