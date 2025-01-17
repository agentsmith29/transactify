""" Class that represents the movement (in/out) of cash in the store. """

from django.db import models
from django.utils import timezone

from store.webmodels.StoreCash import StoreCash
from store.webmodels.Customer import Customer
from django.contrib.auth.models import User

class StoreCashMovement(models.Model):
    """ Class that represents the movement (in/out) of cash in the store. """
    # The current cash in the store
    cash = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    # Amount of money that was moved
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # The type of movement (deposit, withdraw, cashout), set in the child classes
    movement_type = models.CharField(max_length=10)
    # The time the movement was created
    created_at = models.DateTimeField(default=timezone.now)
    # The user that initiated the movement
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        return f"Store Cash Movement: {self.amount} ({self.movement_type})"
        