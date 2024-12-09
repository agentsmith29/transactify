from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from cashlessui.models import Customer
from ..webmodels.CustomerDeposit import CustomerDeposit
import json

class ViewSingleCustomer(View):
    template_name = 'store/customer_detail.html'

    #def __init__(self):
    #    self.controller = CustomerController(nfc_reader=nfc_reader, keypad=keypad, oled=oled)

    def get(self, request, card_number=None):
        """
        Handle GET requests to display customer details and deposit history.
        """
        if card_number is None:
            card_number = request.GET.get('card_number')

        customer = get_object_or_404(Customer, card_number=card_number)
        deposits = CustomerDeposit.objects.filter(customer=customer).order_by('-timestamp')

        return render(request, self.template_name, {
            'customer': customer,
            'deposits': deposits,
        })

    def post(self, request, card_number=None):
        """
        Handle POST requests to update the customer's balance by adding a deposit.
        """
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            amount = data.get('amount')

            if not amount or float(amount) <= 0:
                return JsonResponse({'error': 'Invalid amount'}, status=400)

            # Fetch the customer
            customer = get_object_or_404(Customer, card_number=card_number)

            # Create a new deposit record
            deposit = CustomerDeposit.objects.create(customer=customer, amount=amount)

            # Update the customer's balance
            customer.balance += Decimal(amount)
            customer.save()

            card_number, _ = asyncio.run(self.controller.nfc_write(
                f"Deposit of EUR {amount} successful. New balance: EUR {customer.balance:.2f}"
            ))

            cn, text = asyncio.run(self.controller.nfc_read())
            print(f"Card number: {cn}, Text: {text}")



            return JsonResponse({'message': 'Deposit successful'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
