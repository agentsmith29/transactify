from rest_framework import serializers
from django.contrib.auth.models import User
from cashlessui.models import Customer
from store.webmodels.CustomerBalance import CustomerBalance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class CustomerBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBalance
        fields = ['balance', 'total_deposits', 'total_purchases', 'last_changed']

class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nested serializer for User fields
    balance = serializers.SerializerMethodField()  # Custom method for CustomerBalance

    class Meta:
        model = Customer
        fields = ['user', 'card_number', 'issued_at', 'balance']

    def get_balance(self, obj):
        """Retrieve the balance details for the customer."""
        customer_balance = CustomerBalance.objects.filter(customer=obj).first()
        return CustomerBalanceSerializer(customer_balance).data if customer_balance else None
