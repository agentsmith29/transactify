import json

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt, ensure_csrf_cookie

from store.webmodels.Customer import Customer

from ..webmodels.CustomerDeposit import CustomerDeposit
from ..webmodels.CustomerPurchase import CustomerPurchase
from store.helpers.ManageStockHelper import StoreHelper
from store import StoreLogsDBHandler 


from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import models
from datetime import datetime, timedelta


from transactify_service.settings import CONFIG
import logging

#from ..apps import hwcontroller
@method_decorator(login_required, name='dispatch')
class SingleCustomerView(View):
    template_name = 'store/customer.html'

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f"{CONFIG.webservice.SERVICE_NAME}.webviews.{self.__class__.__name__}")
        super().__init__(**kwargs)
    

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, card_number=None):
        """+
        Handle GET requests to display customer details and deposit history.
        """
        if card_number is None:
            card_number = request.GET.get('card_number')

        customer = get_object_or_404(Customer, card_number=card_number)
        balance = customer.balance


        return render(request, self.template_name, {
            'auth_user': request.user,
            'customer': customer,
            #'balance': balance,
            #'total_deposits': customer.total_deposits,
            #'total_purchases': customer.total_purchases,
            'deposits': customer.get_deposits(),
            'total_deposits_amount': customer.get_total_deposit_amount(),
            'purchases': customer.get_purchases(),
            'total_purchases_amount': customer.get_total_purchase_amount(),
            'store_profit': customer.get_generated_profit(),
            'store_profit_change_percent': customer.get_monthly_generated_profit_change(),
            # percetgae change in the last month
            'deposit_change_percent': customer.get_monthly_deposit_percentage_change(),
            'purchase_change_percent': customer.get_monthly_purchase_percentage_change(),
            #'chart_data': customer.chart_data
        })
   

    def post(self, request, card_number=None):
        """
        Handle POST requests to update the customer's balance by adding a deposit.
        """
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            amount = data.get('deposit_amount')

            if not amount or float(amount) <= 0:
                return JsonResponse({'error': 'Invalid amount'}, status=400)

            # Fetch the customer
            customer = get_object_or_404(Customer, card_number=card_number)
            
            # Create a new deposit record
            # Log the deposit
            response, customer_deposit = StoreHelper.customer_add_deposit(customer, amount, self.logger )

            # Update the customer's balance
            #customer.increment_balance(CustomerBalance, amount)
            #customer.save()

            #card_number, _ = asyncio.run(self.controller.nfc_write(
            #    f"Deposit of EUR {amount} successful. New balance: EUR {customer.balance:.2f}"
            #))

            #cn, text = asyncio.run(self.controller.nfc_read())
            #print(f"Card number: {cn}, Text: {text}")
            return JsonResponse({'message': 'Deposit successful'}, status=200)

        except json.JSONDecodeError:
            print("Invalid JSON data")
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
