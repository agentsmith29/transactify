from typing import Any
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import User
from store.webmodels.APIKey import APIKey
import uuid 

class Customer(models.Model):
    """
        Represents a customer shared across all stores.
        Linked to the default Django User model.
        - **customer** (*Customer*): The customer who made the deposit. Links to *Customer*.
        - **balance** (*Decimal*): The balance of the customer after the deposit.
        - **total_deposits** (*int*): The total amount of deposits made by the customer.
        - **total_purchases** (*int*): The total amount of purchases made by the customer.
        - **last_changed** (*DateTime*): The date and time the balance was last changed.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer")
    card_number = models.CharField(primary_key=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deposits = models.PositiveIntegerField(default=0)
    total_purchases = models.PositiveIntegerField(default=0)
    last_changed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.user.first_name} {self.customer.user.last_name} has {self.balance}"
    

    def get_balance(self, balance_model: Any) -> float:
        return balance_model.objects.get(customer=self).balance
    
    def set_balance(self, balance_model: models.Model, new_balance: float) -> None:
        """
        Set the balance of the customer. Don't forget to save the balance model after calling this method.
        """
        balance = balance_model.objects.get(customer=self)
        balance.balance = new_balance
        return balance


    def generate_api_key_for_user(user):
        """
        Generate an API key for a given user.
        """
        api_key, created = APIKey.objects.get_or_create(user=user)
        if not created:
            api_key.key = uuid.uuid4()  # Regenerate key if it already exists
            api_key.save()
        return api_key.key


    def get_all_deposits(self, deposit_model: models.Model) -> list:
        return deposit_model.objects.filter(customer=self).order_by('-deposit_date')
    
    def get_all_deposits_aggregated(self, deposit_model: models.Model) -> float:
        dagg = deposit_model.objects.filter(customer=self).aggregate(
            total=Coalesce(
                models.Sum(
                    models.ExpressionWrapper(
                        models.F('amount'),
                        output_field=models.DecimalField()), 
                    ),
                    Value(0, output_field=models.DecimalField())
                )
            )['total']
        return dagg
    
    def get_all_purchases(self, purchase_model: models.Model) -> list:
        return purchase_model.objects.filter(customer=self).order_by('-purchase_date')
    
    def get_all_purchases_aggregated(self, purchase_model: models.Model) -> float:
        # purchases are purchase_price*quantity
        pagg = purchase_model.objects.filter(customer=self).aggregate(
            total=Coalesce(
                models.Sum(
                    models.ExpressionWrapper(
                        models.F('purchase_price') * models.F('quantity'),
                        output_field=models.DecimalField()), 
                    ),
                    Value(0, output_field=models.DecimalField())
                )
            )['total']
        return pagg
    
    def __str__(self):
        return f"Customer: {self.user.username}"
