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
    #class Meta:
    #    #db_table = "customer"  # This will ensure the table name is "customer"
    #    app_label = "customer"  # This will ensure the table is routed to the correct database
        
    """
    Represents a customer shared across all stores.
    Linked to the default Django User model.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer")
    card_number = models.CharField(primary_key=True)
    issued_at = models.DateTimeField(auto_now_add=True)

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
        #dagg = deposit_model.objects.filter(customer=self).aggregate(
        #    models.Sum('amount'), Value(0)
        #    )['amount__sum']
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
        print(f"******* get_all_deposits_aggregated: {dagg}")
        return dagg
    
    def get_all_purchases(self, purchase_model: models.Model) -> list:
        return purchase_model.objects.filter(customer=self).order_by('-purchase_date')
    
    def get_all_purchases_aggregated(self, purchase_model: models.Model) -> float:
        # purchases are purchase_price*quantity
        dagg = purchase_model.objects.filter(customer=self).aggregate(
            total=Coalesce(
                models.Sum(
                    models.ExpressionWrapper(
                        models.F('purchase_price') * models.F('quantity'),
                        output_field=models.DecimalField()), 
                    ),
                    Value(0, output_field=models.DecimalField())
                )
            )['total']
        print(f"******* get_all_purchases_aggregated: {dagg}")
        return dagg
    
    def __str__(self):
        return f"Customer: {self.user.username}"
