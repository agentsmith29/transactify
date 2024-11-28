from django.db import models
from cashlessui.models import Customer

class CustomerBalance(models.Model):
    """Represents a deposit made by a customer."""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_constraint=False  )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_changed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} has {self.balance}"


