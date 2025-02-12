from django.contrib.auth.models import User
from django.db import models

from transactify_service.settings import CONFIG

class CustomerConfig(models.Model):
    id = models.AutoField(primary_key=True)
    auto_deposit = models.BooleanField(default=bool(CONFIG.customer.AUTO_DEPOSIT))
    customer_enabled = models.BooleanField(default=True)