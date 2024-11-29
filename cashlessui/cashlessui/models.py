from typing import Any
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# class CUser(AbstractUser):
   
#     def save(self, *args, **kwargs):
#         """Auto-generate the username based on first_name, last_name, and an incrementing number."""
#         if not self.username:
#             base_username = f"{self.first_name[0].lower()}.{self.last_name.lower()}"
#             # Check if a user with the base username already exists
#             similar_usernames = User.objects.filter(username__startswith=base_username).count()
#             self.username = f"{base_username}{similar_usernames + 1}"
#         super().save(*args, **kwargs)

class Customer(models.Model):
    """
    Represents a customer shared across all stores.
    Linked to the default Django User model.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer")
    card_number = models.CharField(primary_key=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    #balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def get_balance(self, balance_model: Any) -> float:
        return balance_model.objects.get(customer=self).balance
    
    def set_balance(self, balance_model: Any, new_balance: float) -> None:
        """
        Set the balance of the customer. Don't forget to save the balance model after calling this method.
        """
        balance = balance_model.objects.get(customer=self)
        balance.balance = new_balance
        return balance
    
    def increment_balance(self, balance_model: Any, amount: float) -> None:
        balance = balance_model.objects.get(customer=self)
        balance.balance += amount
        return balance

    def decrement_balance(self, balance_model: Any, amount: float) -> None:
        balance = balance_model.objects.get(customer=self)
        balance.balance -= amount
        return balance


    def __str__(self):
        return f"Customer: {self.user.username}"
