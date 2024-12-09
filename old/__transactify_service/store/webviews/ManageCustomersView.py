import os
import json
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.contrib.auth.models import User

from cashlessui.models import Customer
from ..webmodels.CustomerDeposit import CustomerDeposit
from ..webmodels.CustomerBalance import CustomerBalance
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
import requests
from django.conf import settings
from django.utils.decorators import method_decorator


#from ..apps import hwcontroller
from django.views.decorators.csrf import csrf_protect, csrf_exempt, ensure_csrf_cookie

from .ManageCustomerHelper import ManageCustomerHelper

class ManageCustomersView(View):
    """Class-based view to handle customer-related operations."""

    def __init__(self):
        pass
    
    def get_all_customers(self):
        """Returns all customers."""
        return Customer.objects.all()
    
    def create_new_customer(self, username, first_name, last_name, email, balance, card_number):
        """Creates and saves a new customer."""
        # Create the associated User object
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        group = Group.objects.get(name="Customer")

        # Create the Customer object linked to the User
        customer = Customer.objects.create(
            user=user,
            card_number=card_number,
            issued_at=datetime.now(),
        )
        customer.user.groups.add(group)
        customer.save()

        # Log the initial deposit
        
        customer_balance, inst = CustomerBalance.objects.get_or_create(
            customer=customer
        )
        customer_balance.total_deposits += 1
        deposit = CustomerDeposit.objects.create(
            customer=customer,
            customer_balance=customer_balance.balance,
            amount=balance,
            deposit_date=datetime.now()
        )
        customer_balance.balance = balance
        customer_balance.save()

       
        
        return customer, deposit

    @method_decorator(ensure_csrf_cookie)
    #@ensure_csrf_cookie
    def get(self, request):
        """Handle GET requests to display all customers."""
        customers = self.get_all_customers()
        balance = []
        for customer in customers:
            balance.append(CustomerBalance.objects.get(customer=customer).balance)
        #roles = Group.objects.all()
        # hwcontroller.view_start_card_management()
        return render(request, 'store/manage_customers.html', {'customers': zip(customers, balance)})
    
    #@method_decorator(csrf_protect)
    #@method_decorator(csrf_exempt)
    def post(self, request):
        """Handle POST requests to add a new customer."""     
        #csrf_secret = request.COOKIES.get(settings.CSRF_COOKIE_NAME, None)
        #print(request.META.get('HTTP_X_CSRFTOKEN'))  # Print CSRF token from headers
        #print(request.COOKIES.get('csrftoken'))  # Print CSRF token from cookies  
        try:
            data = json.loads(request.body)
            print(f"********* data: {data}\n\n\n")

            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            # convert balance to Decimal
            balance = float(data.get('balance'))

            #first_name = request.POST.get('first_name')
            #last_name = request.POST.get('last_name')
            #email = request.POST.get('email')
            #balance = request.POST.get('balance')

            # Validate the required fields
            if not first_name or not last_name or not email or balance is None:
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)
            username = f"{first_name[0].lower()}.{last_name.lower()}"
            
            #hwcontroller.view_present_card(username, email, balance)

            # Trigger NFC read
            print("Waiting for NFC card...")
            card_number, content = "1234", "" #hwcontroller.hwif.nfc_reader.read_block()
            # create a request 
            terminal_url = f"{os.getenv('TERMINAL_SERVICES')}/terminal/api/read/nfc-blocking/"
            json_response = requests.get(terminal_url)
            if json_response.status_code != 200:
                return JsonResponse({'status': 'error', 'message': 'Failed to read NFC card'})
            card_number = json_response.json().get('id')
            content = json_response.json().get('content')

            content = "Some content"
            print(f"Card number: {card_number}, Content: {content}")

            # Create and save the new customer
            customer, deposit_entry = ManageCustomerHelper.create_new_customer(username, first_name, last_name, email, balance, card_number)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
