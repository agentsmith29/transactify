from django.contrib.auth.models import User
from django.db import models

from transactify_service.settings import CONFIG
from django import forms

class CustomerConfig(models.Model):
    id = models.AutoField(primary_key=True)
    auto_deposit = models.BooleanField(default=bool(CONFIG.customer.AUTO_DEPOSIT))
    customer_enabled = models.BooleanField(default=True)

    # EMail Settings
    email_enabled = models.BooleanField(default=False)
    email_on_deposit = models.BooleanField(default=True)
    email_on_purchase = models.BooleanField(default=True)
    email_on_low_balance = models.BooleanField(default=True)
    email_on_disabled = models.BooleanField(default=True)
    email_on_enabled = models.BooleanField(default=True)
    email_on_deleted = models.BooleanField(default=True)
    email_on_balance_change = models.BooleanField(default=True)
    email_on_purchase_change = models.BooleanField(default=True)

    #@property
    #def form_config(self):
    #    return ConfigForm(instance=self)

#class ConfigForm(forms.ModelForm):
#    class Meta:
#        model = CustomerConfig
#        fields = "__all__"  # Include all fields