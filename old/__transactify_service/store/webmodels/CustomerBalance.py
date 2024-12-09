from django.db import models
from cashlessui.models import Customer

class CustomerBalance(models.Model):
    """Represents a deposit made by a customer.
    Attributes:
    - **customer** (*Customer*): The customer who made the deposit. Links to *Customer*.
    - **balance** (*Decimal*): The balance of the customer after the deposit.
    - **total_deposits** (*int*): The total amount of deposits made by the customer.
    - **total_purchases** (*int*): The total amount of purchases made by the customer.
    - **last_changed** (*DateTime*): The date and time the balance was last changed.
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_constraint=False  )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deposits = models.PositiveIntegerField(default=0)
    total_purchases = models.PositiveIntegerField(default=0)
    last_changed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.user.first_name} {self.customer.user.last_name} has {self.balance}"


