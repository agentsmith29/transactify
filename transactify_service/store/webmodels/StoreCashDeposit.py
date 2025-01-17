""" Represent a deposit of private money into the store. Inherited form StoreCashMovement"""

from django.db import models
from django.utils import timezone

from store.webmodels.StoreCashMovement import StoreCashMovement
from store.webmodels.Customer import Customer
from .ProductRestock import ProductRestock
from decimal import Decimal

from django.db import transaction

class StoreCashDeposit(StoreCashMovement):
    """ Represent a deposit of private money into the store. Inherited form StoreCashMovement"""
    product_restock = models.ForeignKey(ProductRestock, on_delete=models.CASCADE)

    def __str__(self):
        return f"Store Cash Deposit: {self.amount} ({self.created_at})"
    
    def save(self, *args, **kwargs):
        from store.webmodels.StoreCash import StoreCash
        """ Override the save method to update the cash in the store """
        # check if the store cash exists
        with transaction.atomic():
            if not StoreCash.objects.exists():
                store_cash = StoreCash.objects.create()
            else:
                store_cash = StoreCash.objects.last()

            if not self.pk:
                store_cash.cash =  Decimal(store_cash.cash) + Decimal(self.amount)
                store_cash.last_updated = timezone.now()
                store_cash.save()

            self.movement_type = 'deposit'
            self.cash = store_cash.cash
            super().save(*args, **kwargs)