from django.db import models
from store.webmodels.Customer import Customer

class CustomerDeposit(models.Model):
    """Represents a deposit made by a customer.
    
    Attributes:
    - **customer** (*Customer*): The customer who made the deposit. Links to *Customer*.
    - **amount** (*Decimal*): The amount the customer deposited.
    - **customer_balance** (*Decimal*): The customer's balance after the deposit.
    - deposit_date (*DateTime*): The date the deposit was made.
    """
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


