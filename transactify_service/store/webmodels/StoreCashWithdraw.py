""" Represents a StoreCashMovement where money has been ued to purchase products. """

from django.db import models
from django.utils import timezone

from store.webmodels.StoreCashMovement import StoreCashMovement
from store.webmodels.Customer import Customer
from .ProductRestock import ProductRestock
from decimal import Decimal

class StoreCashWithdraw(StoreCashMovement):
    """ Represents a StoreCashMovement where money has been ued to purchase products. """
    product_restock = models.ForeignKey(ProductRestock, on_delete=models.CASCADE)

    def __str__(self):
        return f"Store Cash Withdraw: {self.amount} ({self.created_at})"
    
    def save(self, *args, **kwargs):
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