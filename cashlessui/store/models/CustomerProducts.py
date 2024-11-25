from django.db import models
from .StoreProducts import StoreProduct
from .Customer import Customer

class CustomerPurchase(models.Model):
    """Represents a customer purchasing a product."""
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(StoreProduct, on_delete=models.CASCADE, related_name="purchases")
    quantity = models.PositiveIntegerField()
    sell_price = models.DecimalField(max_digits=10, decimal_places=2)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="purchases")
    sell_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} purchased {self.quantity} x {self.product.name}"


