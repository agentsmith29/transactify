import asyncio
import sys

import json

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.db import models
from django.conf import settings

sys.path.append('..')

#from .models import Product, StockProductPurchase, StockProductSale, Customer, CustomerDeposit
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
#from .models import Product
from .webmodels.StoreProduct import StoreProduct
from cashlessui.models import Customer
from .webmodels.CustomerDeposit import CustomerDeposit
from .webmodels.CustomerPurchase import CustomerPurchase
from .webmodels.ProductRestock import ProductRestock
from .webmodels.Store import Store
from .webmodels.StoreProduct import StoreProduct



from decimal import Decimal
from django.db.models import Sum, F

from PIL import Image, ImageDraw, ImageFont, ImageOps
import PIL.Image


#from .controller.CustomerController import CustomerController

from luma.core.interface.serial import spi
from luma.oled.device import ssd1322 as OLED
from .controller.KeyPad import KeyPad 
from .controller.mfrc522.SimpleMFRC522 import SimpleMFRC522

from time import time
from datetime import datetime

import sys

#from .controller.HardwareController import HardwareController
#hwcontroller = HardwareController()




def view_stock(request):
    product_infos = Product.objects.all()
    return render(request, 'store/view_stock.html', {'products': product_infos})


def add_new_product(request):
    if request.method == 'POST':
        # Members for the new product (ProductInfo)
        ean = request.POST.get('ean')
        name = request.POST.get('name')
        resell_price = Decimal(request.POST.get('resellprice'))

        Product.objects.create(ean=ean, name=name, stock_quantity=0, resell_price=resell_price)

        return HttpResponse(f"Product '{name}' added successfully.")
    return render(request, 'store/add_product.html')


class oldManageProductsView(View):
    template_name = 'store/manage_products.html'

    def get(self, request):
        
        """Handle GET requests to display all products."""
        products = Product.objects.all()
        return render(request, self.template_name, {'products': products})

    def post(self, request):
        """Handle POST requests for adding or editing products."""
            
        ean = request.POST.get('ean')
        name = request.POST.get('name')
        resell_price = request.POST.get('resellprice')
        print(f"********* request.POST: {request.POST}\n\n\n")
        if 'delete_ean' in request.POST:
            ean = request.POST.get('delete_ean')
            print(f"********* Trying to delete product with EAN: {ean}\n\n\n")
            # Delete the product with the given EAN
            Product.objects.filter(ean=ean).delete()
            return redirect('manage_products')
       

        # Create a new product
        product, inst = Product.objects.get_or_create(
            ean=ean
        )
        product.name = name
        product.resell_price = resell_price
        product.save()

        # Redirect to avoid resubmission issues
        return redirect('manage_products')














def add_stock(request):
    if request.method == 'POST':
        ean = request.POST.get('ean')
        quantity = int(request.POST.get('quantity'))
        purchase_price = Decimal(request.POST.get('purchase_price'))
        try:
            # Create a new Product object with the given EAN if it does not exist
            product_info = Product.objects.get(ean=ean)

            #for s in range(stock):
            StockProductPurchase.objects.create(product=product_info,
                                                quantity=quantity,
                                                purchase_price=purchase_price,
                                                total_cost=purchase_price * quantity)
            # Count the number of units of the product with the given EAN
            quantity_bough = StockProductPurchase.objects.aggregate(quantity=Sum('quantity'))['quantity'] or 0
            #StockProductPurchase.objects.filter(product=product_info).count())
            quantity_sold = StockProductSale.objects.filter(product=product_info).count()
            quantity = quantity_bough - quantity_sold

            # Update the stock of the product with the given EAN
            product_info.stock_quantity = quantity
            product_info.save()
        except StockProductPurchase.DoesNotExist:
            return HttpResponse("Error: Product with the given EAN does not exist.")
    return render(request, 'store/add_stock.html', {'products': Product.objects.all(),
                                                    'sales': StockProductSale.objects.all(),
                                                    'purchases': StockProductPurchase.objects.all()})


from .webviews.ManageStock import ManageStock

def make_sale(request):
    if request.method == 'POST':
        ean = request.POST.get('ean')
        quantity = int(request.POST.get('quantity'))
        sale_price = Decimal(request.POST.get('sale_price'))
        customer = request.POST.get('customer')

        try:
            ManageStock.make_sale(ean, quantity, sale_price, customer)
        except StockProductPurchase.DoesNotExist:
            return HttpResponse("Error: Product with the given EAN does not exist.")
    return render(request, 'store/make_sale.html', {
        'products': Product.objects.all()
    })


def view_customers(request):
    """View to list all customers."""

    return render(request, 'store/view_customers.html', {'customers': customers})



# class ManageCustomers(View):
#     """Class-based view to handle customer-related operations."""

#     def __init__(self):
#         pass
    
#     def get_all_customers(self):
#         """Returns all customers."""
#         return Customer.objects.all()
    
#     def create_new_customer(self,name, surname, balance, card_number):
#         """Creates and saves a new customer."""
#         customer = Customer.objects.create(
#             card_number=card_number,
#             name=name,  
#             surname=surname,
#             balance=balance
#         )
#         deposit = CustomerDeposit.objects.create(
#             customer=customer,
#             amount=balance,
#             timestamp=datetime.now()
#         )
#         return customer, deposit
    

#     def get(self, request):
#         """Handle GET requests to display all customers."""
#         customers = self.get_all_customers()
#         hwcontroller.view_start_card_management()
#         return render(request, 'store/view_customers.html', {'customers': customers})

#     def post(self, request):
#         """Handle POST requests to add a new customer."""
#         #try:
#             # Parse JSON data from the request body
#         data = json.loads(request.body)
#         name = data.get('name')
#         surname = data.get('surname')
#         balance = data.get('balance')
        
#         hwcontroller.view_present_card(name, surname, balance)

        
#         # Trigger NFC read
#         print("Waiting for NFC card...")
#         card_number, content = hwcontroller.hwif.nfc_reader.read_block()
#         #card_number, content = ("12345", "Test content")
#         print(f"Card number: {card_number}, Content: {content}")

#         # Create and save the new customer
#         self.create_new_customer(name, surname, balance, card_number)

#         return JsonResponse({'status': 'success'})
#         #except Exception as e:
#         #    print(f"Error: {e}")
#         #    return JsonResponse({'status': 'error', 'message': str(e)})

class CheckNFCStatus(View):
    def get(self, request):
        """
        Check if the NFC reading process is complete.
        """
        nfc_complete = request.session.get('nfc_complete', False)
        card_number = request.session.get('card_number', None)
        return JsonResponse({'nfc_complete': nfc_complete, 'card_number': card_number})

class ViewSingleCustomer(View):
    template_name = 'store/customer_detail.html'

    def __init__(self):
        pass
        #self.controller = CustomerController(nfc_reader=nfc_reader, keypad=keypad, oled=oled)

    def get(self, request, card_number=None):
        """
        Handle GET requests to display customer details and deposit history.
        """
        if card_number is None:
            card_number = request.GET.get('card_number')

        customer = get_object_or_404(Customer, card_number=card_number)
        deposits = CustomerDeposit.objects.filter(customer=customer)#.order_by('-deposit_date')
        purchases = CustomerPurchase.objects.filter(customer=customer)#.order_by('-purchase_date')

        return render(request, self.template_name, {
            'customer': customer,
            'deposits': deposits,
            'purchases': purchases
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

            card_number, _ = hwcontroller.nfc_reader.nfc_write(
                f"Deposit of EUR {amount} successful. New balance: EUR {customer.balance:.2f}"
            )

            cn, text = asyncio.run(self.controller.nfc_read())
            print(f"Card number: {cn}, Text: {text}")



            return JsonResponse({'message': 'Deposit successful'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

class UpdateCustomerBalance(View):
    def post(self, request, card_number):
        """
        Handle POST requests to update the customer's balance.
        """
        #try:
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
        customer.balance +=  Decimal(amount)
        customer.save()

        return JsonResponse({'message': 'Deposit successful'}, status=200)

       # except json.JSONDecodeError:
       #     return JsonResponse({'error': 'Invalid JSON data'}, status=400)
       # except Exception as e:
       #     return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
        
class NFCReadView(View):
    def __init__(self):
        pass
        #self.controller = CustomerController(nfc_reader=nfc_reader, keypad=keypad, oled=oled)

    def get(self, request):
        """
        Blocking NFC read to fetch customer details.
        """
        try:
            # Blocking NFC reader
            start_time = time()
            timeout = 30  # Timeout in seconds
            card_number = None

            print("Waiting for NFC card...")

            while not card_number and time() - start_time < timeout:
                # Simulate NFC reader blocking call
                card_number, text = self.controller.reader.read()

            if not card_number:
                return JsonResponse({'status': 'timeout', 'message': 'No card detected. Please try again.'})

            # Fetch the customer based on the card number
            customer = get_object_or_404(Customer, card_number=card_number)

            # Mark the session as complete and return customer data
            request.session['nfc_complete'] = True
            request.session['customer_id'] = customer.card_number
            return JsonResponse({
                'status': 'success',
                'customer_id': customer.card_number,
                'customer_name': f"{customer.name} {customer.surname}",
            })

        except Customer.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Customer not found.'})
        except Exception as e:
            print(f"Error during NFC read: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred during NFC reading.'})
        
class PresentCardView(View):
    template_name = 'store/present_card.html'

    def get(self, request):
        """
        Display the 'Present Card' page.
        """
        # Clear any previous NFC session data
        request.session['nfc_complete'] = False
        request.session['customer_id'] = None
        return render(request, self.template_name)


# old
def view_financial_summary(request):
    #total_revenue = Sale.objects.aggregate(total_revenue=Sum('revenue'))['total_revenue'] or 0
    #total_expenses = Sale.objects.aggregate(total_expense=Sum('expense'))['total_expense'] or 0
    #total_expenses = Stock.objects.aggregate(total_expense=Sum(F('quantity') * F('unit_price')))['total_expense'] or 0
    #total_earnings = total_revenue - total_expenses
    products_sold = StockProductPurchase.objects.filter(type='SOLD').all()
    products_bought = StockProductPurchase.objects.filter(type='BOUGHT').all()

    #sales = Sale.objects.all()
    #stock = Stock.objects.all()

    context = {
        #    'total_revenue': total_revenue,
        #    'total_expenses': total_expenses,
        #    'total_earnings': total_earnings,
        'products_sold': products_sold,
        'products_bought': products_bought,
        #    #'stock': stock,
    }
    return render(request, 'store/view_financial_summary.html', context)
