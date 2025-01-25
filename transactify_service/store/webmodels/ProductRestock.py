from django.db import models
from .StoreProduct import StoreProduct
from .StoreCashMovement import StoreCashMovement

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

import logging

class ProductRestock(models.Model):
    """Represents re
    stocking a product in a store.
    
    Attributes:
    - **id** (*int*): The primary key of the restock.
    - **product** (*StoreProduct*): The product that was restocked. Links to *StoreProduct*.
    - **quantity** (*int*): The quantity of the product that was restocked.
    - **purchase_price** (*Decimal*): The price at which the product was restocked.
    - **total_cost** (*Decimal*): The total cost of the restock.
    - restock_date (*DateTime*): The date and time the restock was made.
    """
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(StoreProduct, on_delete=models.CASCADE, related_name="stock_purchases")
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    restock_date = models.DateTimeField(auto_now_add=True)
   
    cash_movement_type = models.ForeignKey(StoreCashMovement, on_delete=models.CASCADE, null=True)


    def get_all_restocks(product: StoreProduct):
        return ProductRestock.objects.filter(product=product)
    
    def get_all_restocks_aggregated(product: StoreProduct, logger: logging.Logger):
        _ara = ProductRestock.objects.filter(product=product).aggregate(models.Sum('quantity'))['quantity__sum']
        logger.debug(f"Getting all restocks for product {product.name}: {_ara}")
        return _ara

    def save(self, *args, **kwargs):
        from .ProductInventory import ProductInventory
        """Override save to automatically create or update ProductInventory."""
        super().save(*args, **kwargs)
        # Check if a corresponding ProductInventory exists
        inventory, created = ProductInventory.objects.get_or_create(restock=self)
        if created:
            # Initialize remaining_quantity with the restock quantity
            inventory.remaining_quantity = self.quantity
        else:
            # Update the remaining_quantity if the restock quantity changes
            inventory.remaining_quantity += self.quantity
        inventory.save()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} restocked."
