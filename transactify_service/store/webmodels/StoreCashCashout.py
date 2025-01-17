""" Represents a StoreCashMovement where money has been withdrawn from the store. """

from django.db import models
from django.utils import timezone

from store.webmodels.StoreCashMovement import StoreCashMovement
from store.webmodels.Customer import Customer
from decimal import Decimal

class StoreCashCashout(StoreCashMovement):
    """ Represents a StoreCashMovement where money has been withdrawn from the store. """
    def __str__(self):
        return f"Store Cash Cashout: {self.amount} ({self.created_at})"
    
    def save(self, *args, **kwargs):
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