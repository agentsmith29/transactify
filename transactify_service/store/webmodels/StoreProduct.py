from django.db import models
from decimal import Decimal

class StoreProduct(models.Model):
    """Represents a product bound to a specific store."""
    ean = models.CharField(primary_key=True, unique=True, null=False)  # EAN code
    name = models.CharField(max_length=100, default="Generic Product")
    stock_quantity = models.PositiveIntegerField(default=0)
    discount = models.DecimalField(max_digits=10, default = 0, decimal_places=2) # In percent
    resell_price = models.DecimalField(max_digits=10, default = 0, decimal_places=2)

    def get_final_price(self):
        rsp: Decimal = self.resell_price * (1 - self.discount)
        # Quantize the result to two decimal places
        return rsp.quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")
    
    def __str__(self):
        return f"{self.name} ({self.ean})"


