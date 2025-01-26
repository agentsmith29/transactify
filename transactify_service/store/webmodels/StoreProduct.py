from typing import Iterable
from django.db import models
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum, F, Prefetch, Max, ExpressionWrapper, DecimalField


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



    def calculate_total_profit(self):
        """
        Calculate the total profit for this product.
        """
        from store.webmodels.CustomerPurchase import CustomerPurchase
        result = CustomerPurchase.objects.filter(product=self).aggregate(
            total_profit=Sum(F("profit"))
        )
        return result["total_profit"] or 0  # Return 0 if no result

    def calculate_total_revenue(self):
        """
        Calculate the total revenue from all purchases of this product.
        """
        from store.webmodels.CustomerPurchase import CustomerPurchase
        # Wrap the complex expression in ExpressionWrapper
        revenue_expression = ExpressionWrapper(F("purchase_price") * F("quantity"), output_field=DecimalField())
        result = CustomerPurchase.objects.filter(product=self).aggregate(
            total_revenue=Sum(revenue_expression)
        )
        return result["total_revenue"] or 0  # Return 0 if no result

    def calculate_total_orders(self):
        """
        Calculate the total quantity of orders for this product.
        """
        from store.webmodels.CustomerPurchase import CustomerPurchase
        result = CustomerPurchase.objects.filter(product=self).aggregate(
            total_orders=Sum("quantity")
        )
        return result["total_orders"] or 0  # Return 0 if no result

    

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
                annotated_last_purchase=Max("customerpurchase__purchase_date"),
            )
            .order_by("-total_orders")[:limit]
        )

        results = []
        for product in top_products:
            results.append(
                {
                    "name": product.name,
                    "price": product.final_price,
                    "total_orders": product.calculate_total_orders() or 0,
                    "total_revenue": product.calculate_total_revenue() or Decimal("0.00"),
                    # Include purchases if needed
                    "last_purchase": product.annotated_last_purchase,
                    "total_profit":  product.calculate_total_profit() or Decimal("0.00")

                }
            )
        return results

    def __str__(self):
        return f"{self.name} ({self.ean}) - Stock: {self.stock_quantity}"
