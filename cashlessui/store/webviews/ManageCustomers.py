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

from ..apps import hwcontroller


class ManageCustomers(View):
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
        deposit = CustomerDeposit.objects.create(
            customer=customer,
            customer_balance=customer_balance.balance,
            amount=balance,
            deposit_date=datetime.now()
        )
        customer_balance.balance = balance
        customer_balance.save()

       
        
        return customer, deposit

    def get(self, request):
        """Handle GET requests to display all customers."""
        customers = self.get_all_customers()
        balance = []
        for customer in customers:
            balance.append(CustomerBalance.objects.get(customer=customer).balance)
        #roles = Group.objects.all()
        # hwcontroller.view_start_card_management()
        return render(request, 'store/manage_customers.html', {'customers': zip(customers, balance)})

    def post(self, request):
        """Handle POST requests to add a new customer."""       
        try:
            data = json.loads(request.body)
            print(f"********* data: {data}\n\n\n")
            #if 'delete_user' in data:
            #    card_number = request.POST.get('card_number')
            #    print(f"********* Trying to delete User with card number: {card_number}\n\n\n")
            #    # Delete the product with the given EAN
            #    Customer.objects.filter(card_number=card_number).delete()
            #    return redirect('manage_customers')
        
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            balance = data.get('balance')

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
            card_number, content = hwcontroller.hwif.nfc_reader.read_block()
            content = "Some content"
            print(f"Card number: {card_number}, Content: {content}")

            # Create and save the new customer
            self.create_new_customer(username, first_name, last_name, email, balance, card_number)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
