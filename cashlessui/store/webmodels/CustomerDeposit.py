from django.db import models
from cashlessui.models import Customer

class CustomerDeposit(models.Model):
    """Represents a deposit made by a customer."""
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="deposits",
                                  db_constraint=False 
                                  )
    # Amout the customer deposited
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # The customer's balance after the deposit
    customer_balance = models.DecimalField(max_digits=10, decimal_places=2)
    # The date the deposit was made
    deposit_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} deposited {self.amount}"


