from typing import Iterable
from django.db import models
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum, F, Prefetch


class StoreProduct(models.Model):
    """Represents a product in the store."""
    ean = models.CharField(unique=True, null=False, max_length=13)  # EAN code
    name = models.CharField(max_length=100, default="Generic Product")
    stock_quantity = models.PositiveIntegerField(default=0)  # Auto-calculated if needed
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))  # Percent
    product_fill_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    # Nutritional facts
    nutri_score = models.CharField(max_length=10, null=True, blank=True)
    energy_kcal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    energy_kj = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fat = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    carbohydrates = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sugar = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fiber = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    proteins = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=255, null=True, blank=True)

    # Pricing
    resell_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    #final_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=Decimal("0.00"))

    # Auto-calculated fields
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))  # Derived
    total_orders = models.PositiveIntegerField(default=0)  # Derived

    added_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Override save method to calculate and update final price."""
       # self.final_price = self.calculate_final_price()
        super().save(*args, **kwargs)
    
    @property
    def final_price(self):
        return self.calculate_final_price()

    def calculate_final_price(self):
        if self.discount > 1:
            raise ValueError("Discount must be a percentage value between 0 and 1.")
        
        """Calculate final price after discount."""
        price = self.resell_price * (1 - self.discount)
        return price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def get_top_selling_products(limit: int) -> Iterable[dict]:
        """Fetch top-selling products with pre-aggregated data."""
        from store.webmodels.CustomerPurchase import CustomerPurchase

        # Use aggregation and annotation to avoid N+1 query problems
        top_products = (
            StoreProduct.objects.prefetch_related(
                Prefetch("customerpurchase_set", queryset=CustomerPurchase.objects.all())
            )
            .annotate(
                annotated_total_revenue=Sum(F("resell_price") * F("customerpurchase__quantity")),
                annotated_total_orders=Sum("customerpurchase__quantity"),
            )
            .order_by("-total_orders")[:limit]
        )

        results = []
        for product in top_products:
            results.append(
                {
                    "name": product.name,
                    "price": product.final_price,
                    "total_orders": product.annotated_total_orders or 0,
                    "total_revenue": product.annotated_total_revenue or Decimal("0.00"),
                    # Include purchases if needed
                }
            )
        return results

    def __str__(self):
        return f"{self.name} ({self.ean}) - Stock: {self.stock_quantity}"
