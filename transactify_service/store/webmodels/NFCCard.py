from django.contrib.auth.models import User
from django.db import models

from transactify_service.settings import CONFIG
from django import forms

class NFCCard(models.Model):
    id = models.AutoField(primary_key=True)
    # Type of the cards
    rfid_type = models.CharField()

    # custom attributes
    type = models.CharField(default="Generic Card")

    linked_customer = models.OneToOneField()