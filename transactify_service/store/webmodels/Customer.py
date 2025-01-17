from typing import Any, Union
import json
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from decimal import Decimal
from datetime import datetime, timedelta
from collections import defaultdict

from store.helpers.deprecated import deprecated
from store.webmodels.APIKey import APIKey

class Customer(models.Model):
    """
    Represents a customer shared across all stores.
    Linked to the default Django User model.

    Attributes:
        user (User): The associated Django User instance.
        card_number (str): Primary key, unique card number for the customer.
        issued_at (datetime): The date and time the customer was created.
        balance (Decimal): The current balance of the customer.
        total_deposits (int): Total count of deposits made by the customer.
        total_purchases (int): Total count of purchases made by the customer.
        last_changed (datetime): The timestamp of the last balance change.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer")
    card_number = models.CharField(primary_key=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deposits = models.PositiveIntegerField(default=0)
    total_purchases = models.PositiveIntegerField(default=0)
    last_changed = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    

    def get_deposits(self, date: Union[datetime, tuple[datetime, datetime]] = None) -> models.QuerySet:
        """
        Retrieve all deposits made by the customer.

        Args:
            date (Union[datetime, tuple[datetime, datetime]], optional):
                Specific date or date range for filtering deposits.

        Returns:
            QuerySet: Deposits matching the given criteria.
        """
        from store.webmodels.CustomerDeposit import CustomerDeposit
        try:
            if date is not None and isinstance(date, tuple):
                _dstart, _dend = date
                if not isinstance(_dstart, datetime) or not isinstance(_dend, datetime):
                    raise ValueError("Invalid date range or type.")

                if _dstart > _dend:
                    _dstart, _dend = _dend, _dstart

                return CustomerDeposit.objects.filter(deposit_date__range=(_dstart, _dend), customer=self).order_by('-deposit_date')  # #1: Added `customer=self` to filter by customer
            elif date is not None and isinstance(date, datetime):
                return CustomerDeposit.objects.filter(customer=self, deposit_date=date).order_by('-deposit_date')
            else:
                return CustomerDeposit.objects.filter(customer=self).order_by('-deposit_date')
        except Exception as e:
            print(f"Error getting deposits: {e}")
            return CustomerDeposit.objects.none()

    def get_purchases(self, date: Union[datetime, tuple[datetime, datetime]] = None) -> models.QuerySet:
        """
        Retrieve all purchases made by the customer.

        Args:
            date (Union[datetime, tuple[datetime, datetime]], optional):
                Specific date or date range for filtering purchases.

        Returns:
            QuerySet: Purchases matching the given criteria.
        """
        from store.webmodels.CustomerPurchase import CustomerPurchase
        try:
            if date is not None and isinstance(date, tuple):
                _dstart, _dend = date
                if not isinstance(_dstart, datetime) or not isinstance(_dend, datetime):
                    raise ValueError("Invalid date range or type.")

                if _dstart > _dend:
                    _dstart, _dend = _dend, _dstart

                return CustomerPurchase.objects.filter(purchase_date__range=(_dstart, _dend), customer=self).order_by('-purchase_date')  # #2: Added `customer=self` to filter by customer
            elif date is not None and isinstance(date, datetime):
                return CustomerPurchase.objects.filter(customer=self, purchase_date=date).order_by('-purchase_date')
            else:
                return CustomerPurchase.objects.filter(customer=self).order_by('-purchase_date')
        except Exception as e:
            print(f"Error getting purchases: {e}")
            return CustomerPurchase.objects.none()

    def get_total_deposit_amount(self, date: Union[datetime, tuple[datetime, datetime]] = None) -> float | Decimal:  # #3: Renamed method for clarity
        """
        Calculate the total amount of deposits made by the customer.

        Args:
            date (Union[datetime, tuple[datetime, datetime]], optional):
                Specific date or date range for filtering deposits.

        Returns:
            float: Total deposit amount.
        """
        return self.get_deposits(date).aggregate(total=models.Sum('amount'))['total'] or 0.0

    def get_total_purchase_amount(self, date: Union[datetime, tuple[datetime, datetime]] = None) -> float | Decimal:  # #4: Renamed method for clarity
        """
        Calculate the total amount of purchases made by the customer.

        Args:
            date (Union[datetime, tuple[datetime, datetime]], optional):
                Specific date or date range for filtering purchases.

        Returns:
            float: Total purchase amount.
        """
        return self.get_purchases(date).aggregate(total=models.Sum(models.F('purchase_price') * models.F('quantity')))['total'] or 0.0

 
    def get_generated_profit(self, date: datetime | tuple[datetime, datetime]=None) -> float:
        """
        Calculate the store profit based on the total purchases and deposits made by the customer.

        Args:
            date (Union[datetime, tuple[datetime, datetime]], optional):
                Specific date or date range for filtering transactions.

        Returns:
            float: Store profit.
        """
        try:
            if date is not None and isinstance(date, tuple):
                _dstart, _dend = date
                if not isinstance(_dstart, datetime) or not isinstance(_dend, datetime):
                    raise ValueError("Invalid date range or type.")

                if _dstart > _dend:
                    _dstart, _dend = _dend, _dstart
            # Get the profic of all purchases
            purchases = self.get_purchases(date)
            # field is profit
            total_profit = purchases.aggregate(total=models.Sum('profit'))['total'] or 0.0  
            return total_profit
        
        except Exception as e:
            print(f"Error getting purchases: {e}")
            return 0
    
       

    # =================================================================================================================
    # Changes within a month
    # =================================================================================================================
    def _percentage_month_wrapper(self, func: callable):
        """
            Calculate the percentage change in purchases between the current and previous months.

            Returns:
                float: Percentage change in purchases, rounded to 2 decimal places.
                str: "Infinity" if the previous month had no purchases and current month has purchases.
                    "No change" if both months have no purchases.
        """
        # Get the current date
        today = datetime.now()
        current_month_start = today.replace(day=1)
        previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        previous_month_end = current_month_start - timedelta(days=1)

        # Get the total purchases for the current and previous months using the refined methods
        current_month_val = func(date=(current_month_start, today))
        previous_month_val = func(date=(previous_month_start, previous_month_end))

        # Handle edge cases with no purchases in the previous month
        if previous_month_val == 0:
            if current_month_val > 0:
                return 100    

        current_month_val = float(current_month_val)
        previous_month_val = float(previous_month_val)

        if previous_month_val == 0 and current_month_val > 0:
            return 100
        elif previous_month_val == 0 and current_month_val == 0:
            return 0
        else:
            # Calculate percentage change
            percentage_change = ((current_month_val - previous_month_val) / previous_month_val) * 100

        return round(percentage_change, 2)

    def get_monthly_purchase_percentage_change(self) -> float:
        """
            Calculate the percentage change in purchases between the current and previous months.

            Returns:
                float: Percentage change in purchases, rounded to 2 decimal places.
                str: "Infinity" if the previous month had no purchases and current month has purchases.
                    "No change" if both months have no purchases.
        """
        return self._percentage_month_wrapper(self.get_total_purchase_amount)
    
    def get_monthly_deposit_percentage_change(self) -> float:
        """
            Calculate the percentage change in deposits between the current and previous months.

            Returns:
                float: Percentage change in deposits, rounded to 2 decimal places.
                str: "Infinity" if the previous month had no deposits and current month has deposits.
                    "No change" if both months have no deposits.
        """
        return self._percentage_month_wrapper(self.get_total_deposit_amount)
 
    def get_monthly_generated_profit_change(self) -> float:
        """
            Calculate the percentage change in store profit between the current and previous months.

            Returns:
                float: Percentage change in store profit, rounded to 2 decimal places.
                str: "Infinity" if the previous month had no profit and current month has profit.
                    "No change" if both months have no profit.
        """
        return self._percentage_month_wrapper(self.get_generated_profit)
            


    @property
    def chart_data(self) -> dict:
        """
        Generate chart data summarizing deposits, purchases, and balance over time.

        Returns:
            dict: Aggregated chart data.
        """
        aggregated_data = defaultdict(lambda: {"deposit": 0, "purchase": 0, "balance": 0})

        for deposit in self.get_deposits():
            timestamp = int(deposit.deposit_date.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1e3)
            aggregated_data[timestamp]["deposit"] += float(deposit.amount)
            aggregated_data[timestamp]["purchase"] += float(
                self.get_purchases(date=deposit.deposit_date).aggregate(models.Sum("revenue"))["revenue__sum"] or 0
            )
            aggregated_data[timestamp]["balance"] = float(deposit.customer_balance)

        for purchase in self.get_purchases():
            timestamp = int(purchase.purchase_date.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1e3)
            aggregated_data[timestamp]["purchase"] += float(purchase.revenue)
            aggregated_data[timestamp]["deposit"] += float(
                self.get_deposits(date=purchase.purchase_date).aggregate(models.Sum("amount"))["amount__sum"] or 0
            )
            aggregated_data[timestamp]["balance"] = float(purchase.customer_balance)

        chart_data = {
            "timestamp": [],
            "deposit": [],
            "purchase": [],
            "balance": [],
        }

        for timestamp in sorted(aggregated_data.keys()):
            chart_data["timestamp"].append(timestamp)
            chart_data["deposit"].append(round(aggregated_data[timestamp]["deposit"], 2))
            chart_data["purchase"].append(round(aggregated_data[timestamp]["purchase"], 2))
            chart_data["balance"].append(round(aggregated_data[timestamp]["balance"], 2))

        return chart_data

    @property
    def chart_data_json(self):
        """
        Serialize chart data to a JSON string for rendering in templates.

        Returns:
            str: JSON-formatted chart data.
        """
        return mark_safe(json.dumps(self.chart_data, ensure_ascii=False))

    def generate_api_key_for_user(user):
        """
        Generate a unique API key for the user.

        Args:
            user (User): The user for whom the API key is generated.

        Returns:
            str: The generated API key.
        """
        api_key, created = APIKey.objects.get_or_create(user=user)
        if not created:
            api_key.key = uuid.uuid4()
            api_key.save()
        return api_key.key

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.user.username})"

    @deprecated
    def get_all_deposits(self, deposit_model: models.Model) -> list:
        return deposit_model.objects.filter(customer=self).order_by('-deposit_date')

    @deprecated
    def get_all_purchases(self, purchase_model: models.Model) -> list:
        return purchase_model.objects.filter(customer=self).order_by('-purchase_date')
