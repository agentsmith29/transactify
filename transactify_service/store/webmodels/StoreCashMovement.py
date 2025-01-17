""" Class that represents the movement (in/out) of cash in the store. """

from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User
from decimal import Decimal

from django.db import transaction


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

    def deposit(self, *args, **kwargs):
        from store.webmodels.StoreCash import StoreCash
        """ Override the save method to update the cash in the store """
        # check if the store cash exists
        with transaction.atomic():
            if not StoreCash.objects.exists():
                store_cash = StoreCash.objects.create()
            else:
                store_cash = StoreCash.objects.last()

            store_cash.cash = Decimal(store_cash.cash) + Decimal(self.amount)
            store_cash.last_updated = timezone.now()
            store_cash.save()

            self.movement_type = 'deposit'
            self.cash = store_cash.cash
            super().save(*args, **kwargs)

    def withdraw(self, *args, **kwargs):
        from store.webmodels.StoreCash import StoreCash
        """ Override the save method to update the cash in the store """
        # check if the store cash exists
        if not StoreCash.objects.exists():
            raise Exception("Cannot withdraw without store cash")
        self.movement_type = 'withdraw'
        store_cash = StoreCash.objects.last()
        store_cash.cash =  Decimal(store_cash.cash)  - Decimal(self.amount)
        self.cash = store_cash.cash
        store_cash.last_updated = timezone.now()
        store_cash.save()
        super().save(*args, **kwargs)


    def cashout(self, *args, **kwargs):
        from store.webmodels.StoreCash import StoreCash
        """ Override the save method to update the cash in the store """
        if not StoreCash.objects.exists():
            raise Exception("Cannot cashout without store cash")
        self.movement_type = 'cashout'
        store_cash = StoreCash.objects.last()
        store_cash.cash =  Decimal(store_cash.cash)  - Decimal(self.amount)
        self.cash = store_cash.cash
        store_cash.last_updated = timezone.now()
        store_cash.save()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Store Cash Movement: {self.amount} ({self.movement_type})"
        