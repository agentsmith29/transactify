import json

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt, ensure_csrf_cookie

from store.webmodels.Customer import Customer

from ..webmodels.CustomerDeposit import CustomerDeposit
from ..webmodels.CustomerBalance import CustomerBalance
from ..webmodels.CustomerPurchase import CustomerPurchase
from store.helpers.ManageCustomerHelper import ManageCustomerHelper



class SingleCustomerView(View):
    template_name = 'store/customer_detail.html'

    def __init__(self):
        # We can change later how we talk to the hardware controller
        # self.hwctrl = hwcontroller
        pass

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, card_number=None):
        """
        Handle GET requests to display customer details and deposit history.
        """
        if card_number is None:
            card_number = request.GET.get('card_number')

        customer = get_object_or_404(Customer, card_number=card_number)
        balance = CustomerBalance.objects.get(customer=customer)
        deposits = CustomerDeposit.objects.filter(customer=customer).order_by('-deposit_date')
        purchases = CustomerPurchase.objects.filter(customer=customer).order_by('-purchase_date')
        total_deposits = customer.get_all_deposits_aggregated(CustomerDeposit)
        total_purchases = customer.get_all_purchases_aggregated(CustomerPurchase)

        return render(request, self.template_name, {
            'customer': customer,
            'balance': balance,
            'deposits': deposits,
            'purchases': purchases,
            'total_deposits': total_deposits,
            'total_purchases': total_purchases
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
            customer_balance, inst, deposit_entry = ManageCustomerHelper.customer_add_deposit(customer, amount)

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
