import os
import json
import requests
from datetime import datetime

from store.webmodels.Customer import Customer

from django.http import JsonResponse
from django.views import View
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.utils.decorators import method_decorator


from ..webmodels.CustomerDeposit import CustomerDeposit
from ..webmodels.CustomerBalance import CustomerBalance

from store.helpers.ManageCustomerHelper import ManageCustomerHelper

from django.views.decorators.csrf import csrf_protect, csrf_exempt, ensure_csrf_cookie



class ManageCustomersView(View):
    """Class-based view to handle customer-related operations."""

    def __init__(self):
        pass
    
    def get_all_customers(self):
        """Returns all customers."""
        return Customer.objects.all()
    
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
            terminal_url = f"{os.getenv('TERMINAL_SERVICES')}/api/read/nfc-blocking/"
            json_response = requests.get(terminal_url)
            if json_response.status_code != 200:
                return JsonResponse({'status': 'error', 'message': 'Failed to read NFC card'})
            card_number = json_response.json().get('id')
            content = json_response.json().get('content')

            content = "Some content"
            print(f"Card number: {card_number}, Content: {content}")

            # Create and save the new customer
            customer, customer_balance, deposit_entry = ManageCustomerHelper.create_new_customer(username, first_name, last_name, email, balance, card_number)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(f"Error: {e}")
            # print statck trace
            import traceback
            traceback.print_exc()

            return JsonResponse({'status': 'error', 'message': str(e)})
