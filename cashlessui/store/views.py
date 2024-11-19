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

from .models import Product, StockProductPurchase, StockProductSale, Customer, CustomerDeposit
from decimal import Decimal
from django.db.models import Sum, F

from PIL import Image, ImageDraw, ImageFont, ImageOps
import PIL.Image


#from .controller.CustomerController import CustomerController

from luma.core.interface.serial import spi
from luma.oled.device import ssd1322 as OLED
from controller.KeyPad import KeyPad 
from mfrc522.SimpleMFRC522 import SimpleMFRC522

from time import time
from datetime import datetime

import sys

from .HardwareController import HardwareController
from .controller.HardwareInterface import HardwareInterface
hwcontroller = HardwareController()




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

from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product

class ManageProductsView(View):
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
    return render(request, 'store/add_stock.html', {'products': Product.objects.all()})


def make_sale(request):
    if request.method == 'POST':
        ean = request.POST.get('ean')
        quantity = int(request.POST.get('quantity'))
        sale_price = Decimal(request.POST.get('sale_price'))
        customer = request.POST.get('customer')

        try:
            product_info = Product.objects.get(ean=ean)
            for s in range(quantity):
                StockProductSale.objects.create(product_info=product_info,
                                                quantity=1,
                                                sale_price=sale_price,
                                                sold_to=customer)

            quantity_bough = StockProductPurchase.objects.filter(product=product_info).count()
            quantity_sold = StockProductSale.objects.filter(product=product_info).count()
            quantity = quantity_bough - quantity_sold

            # Update the stock of the product with the given EAN
            product_info.stock_quantity = quantity
            product_info.save()

        except StockProductPurchase.DoesNotExist:
            return HttpResponse("Error: Product with the given EAN does not exist.")
    return render(request, 'store/make_sale.html', {
        'products': Product.objects.all()
    })


def view_customers(request):
    """View to list all customers."""

    return render(request, 'store/view_customers.html', {'customers': customers})



class ViewCustomers(View):
    """Class-based view to handle customer-related operations."""

    def __init__(self):
        pass
    
    def get_all_customers(self):
        """Returns all customers."""
        return Customer.objects.all()
    
    def create_new_customer(self,name, surname, balance, card_number):
        """Creates and saves a new customer."""
        customer = Customer.objects.create(
            card_number=card_number,
            name=name,  
            surname=surname,
            balance=balance
        )
        deposit = CustomerDeposit.objects.create(
            customer=customer,
            amount=balance,
            timestamp=datetime.now()
        )
        return customer, deposit
    
    def oled_view_start(self):
        oled = hwcontroller.hwif.oled
        # Ensure the image mode matches the display's mode
        width = oled.width
        height = oled.height
        image = Image.new(oled.mode, (width, height))  # Use oled.mode for compatibility
        draw = ImageDraw.Draw(image)

        font_large = ImageFont.load_default(size=12)
        font_small = ImageFont.load_default(size=10)

        # Load and resize the NFC symbol image
        try:
            cmd_symbol = PIL.Image.open(r"/home/pi/workspace/cashless/cashlessui/static/icons/card-heading.png")
            cmd_symbol = cmd_symbol.convert('RGB')
            cmd_symbol = ImageOps.invert(cmd_symbol)
        except Exception as e:
            print(f"Error loading NFC symbol: {e}")
            return

        # Header Section
        header_height = 20
        header_text = f"Card Management"
        draw.text((20, 1), header_text, font=font_large, fill=(255,255,255))  # Leave space for NFC symbol

        # Paste the NFC symbol into the header
        image.paste(cmd_symbol, (0, 0))  # Paste at (2, 2) in the top-left corner

        # Divider line
        draw.line([(0, header_height), (width, header_height)], fill=(255,255,255), width=1)

        # Content Section: Display Name, Surname, and Balance
        content_y_start = header_height + 5
        draw.text((30, content_y_start), f"A new card is in preperation. Please wait.", font=font_small,fill=(255,255,255))
        # inster spinner here

        # Update the OLED display
        oled.display(image)
    

    def oled_view_present_card(self, name, surname, balance):
        """
        Display information for issuing a new customer card on a 256x64 OLED.

        Args:
            oled: The initialized OLED display object from luma.oled.device.
            name: Customer's first name.
            surname: Customer's last name.
            balance: Customer's account balance.
            nfc_symbol_path: Path to the NFC symbol image.
        """
        oled = controller.hwif.oled
        # Ensure the image mode matches the display's mode
        width = oled.width
        height = oled.height
        image = Image.new(oled.mode, (width, height))  # Use oled.mode for compatibility
        draw = ImageDraw.Draw(image)

        # Load fonts (adjust paths and sizes as necessary)
        #try:
        #font_large = ImageFont.truetype("arial.ttf", 18)  # Large font for titles
        #font_small = ImageFont.truetype("arial.ttf", 14)  # Smaller font for details
        #except IOError:
        font_large = ImageFont.load_default(size=12)
        font_small = ImageFont.load_default(size=10)

        # Load and resize the NFC symbol image
        try:
            cmd_symbol = PIL.Image.open(r"/home/pi/workspace/cashless/cashlessui/static/icons/card-heading.png")
            cmd_symbol = cmd_symbol.convert('RGB')
            cmd_symbol = ImageOps.invert(cmd_symbol)

            nfc_symbol = PIL.Image.open(r"/home/pi/workspace/cashless/cashlessui/static/icons/rss_24_24.png")
            nfc_symbol = nfc_symbol.convert('RGB')
            nfc_symbol = ImageOps.invert(nfc_symbol)
            #nfc_symbol = nfc_symbol.resize((20, 20))  # Resize the symbol to fit the header
        except Exception as e:
            print(f"Error loading NFC symbol: {e}")
            return

        # Header Section
        header_height = 20
        header_text = f"Issue new Card"
        draw.text((20, 1), header_text, font=font_large, fill=(255,255,255))  # Leave space for NFC symbol

        # Paste the NFC symbol into the header
        image.paste(cmd_symbol, (0, 0))  # Paste at (2, 2) in the top-left corner

        # Divider line
        draw.line([(0, header_height), (width, header_height)], fill=(255,255,255), width=1)

        # Content Section: Display Name, Surname, and Balance
        content_y_start = header_height + 5
        draw.text((30, content_y_start), f"Issue new card for: {name} {surname}", font=font_small,fill=(255,255,255))
        draw.text((30, content_y_start + 12), f"Initial balance: EUR {float(balance):.2f}", font=font_small, fill=(255,255,255))
        draw.text((30, content_y_start + 22), f"Please place your card now.", font=font_small, fill=(255,255,255))
        image.paste(nfc_symbol, (2, content_y_start+5))  # Paste at (2, 2) in the top-left corner

        # Draw NFC readiness indication
        nfc_ready_text = "Tap card on NFC reader..."
        draw.text((160, content_y_start + 40), nfc_ready_text, font=font_small, fill=(255,255,255))

        # Update the OLED display
        oled.display(image)


    def get(self, request):
        """Handle GET requests to display all customers."""
        customers = self.get_all_customers()
        self.oled_view_start()
        return render(request, 'store/view_customers.html', {'customers': customers})

    def post(self, request):
        """Handle POST requests to add a new customer."""
        #try:
            # Parse JSON data from the request body
        data = json.loads(request.body)
        name = data.get('name')
        surname = data.get('surname')
        balance = data.get('balance')
        
        self.oled_view_present_card(name, surname, balance)
        # Trigger NFC read
        print("Waiting for NFC card...")
        card_number, content = controller.nfc_read()
        print(f"Card number: {card_number}, Content: {content}")

        # Create and save the new customer
        self.create_new_customer(name, surname, balance, card_number)

        return JsonResponse({'status': 'success'})
        #except Exception as e:
        #    print(f"Error: {e}")
        #    return JsonResponse({'status': 'error', 'message': str(e)})

class CheckNFCStatus(View):
    def get(self, request):
        """
        Check if the NFC reading process is complete.
        """
        nfc_complete = request.session.get('nfc_complete', False)
        card_number = request.session.get('card_number', None)
        return JsonResponse({'nfc_complete': nfc_complete, 'card_number': card_number})

# class ViewSingleCustomer(View):
#     template_name = 'store/customer_detail.html'

#     def __init__(self):
#         serial_monitor = spi(port = 0, device=1, gpio_DC=23, gpio_RST=24)
#         self.controller = CustomerController(nfc_reader=SimpleMFRC522(), keypad=KeyPad(), oled=OLED(serial_monitor))

#     def get_customer_data(self, customer_id):
#         """
#         Fetches detailed customer data including purchased products and trends.
#         """
#         # Get customer details
#         customer = get_object_or_404(Customer, card_number=customer_id)

#         # Fetch purchased products related to the customer
#         purchased_products = StockProductSale.objects.filter(
#             sold_to=customer
#         ).select_related('product')

#         # Generate chart data for purchase trends
#         purchases_by_month = purchased_products.annotate(
#             month=TruncMonth('sale_date')
#         ).values('month').annotate(total=Sum('quantity')).order_by('month')

#         chart_data = {
#             "labels": [purchase['month'].strftime("%B") for purchase in purchases_by_month],
#             "values": [purchase['total'] for purchase in purchases_by_month],
#         }

#         return {
#             "customer": {
#                 "name": f"{customer.name} {customer.surname}",
#                 "balance": customer.balance,
#                 "issue_date": customer.issued_at,
#             },
#             "purchased_products": purchased_products,
#             "chart_data": chart_data,
#         }

#     def get(self, request):
#         """
#         Handles GET requests to display the customer detail page.
#         """
#         # Display the webpage to present the card, http
        
        
#         #self.controller.view_present_card("name", "surname", 0)
#         ## Trigger NFC read
#         #card_number, _ = asyncio.run(self.controller.nfc_read())
#         #context = self.get_customer_data(card_number)
#         #return render(request, self.template_name, context)
#         return JsonResponse({'redirect_url': '/store/present_card/'})

#     def post(self, request, customer_id):
#         """
#         Handles POST requests for updating customer information or other actions.
#         """
#         # Example: Update customer data (implement your own logic here)
#         customer = get_object_or_404(Customer, id=customer_id)
#         action = request.POST.get('action')

#         if action == 'update_balance':
#             new_balance = float(request.POST.get('balance', customer.balance))
#             customer.balance = new_balance
#             customer.save()
        
#         # Re-fetch the data to reflect updates
#         context = self.get_customer_data(customer_id)
#         return render(request, self.template_name, context)


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
        deposits = CustomerDeposit.objects.filter(customer=customer).order_by('-timestamp')
        purchases = StockProductSale.objects.filter(sold_to=customer).order_by('-sale_date')

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
