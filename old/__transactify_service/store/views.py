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
#from .controller.KeyPad import KeyPad 
#from .controller.mfrc522.SimpleMFRC522 import SimpleMFRC522

from time import time
from datetime import datetime

import sys

#     def __init__(self):
#         pass
#         #self.controller = CustomerController(nfc_reader=nfc_reader, keypad=keypad, oled=oled)

#     def get(self, request):
#         """
#         Blocking NFC read to fetch customer details.
#         """
#         try:
#             # Blocking NFC reader
#             start_time = time()
#             timeout = 30  # Timeout in seconds
#             card_number = None

#             print("Waiting for NFC card...")

#             while not card_number and time() - start_time < timeout:
#                 # Simulate NFC reader blocking call
#                 card_number, text = self.controller.reader.read()

#             if not card_number:
#                 return JsonResponse({'status': 'timeout', 'message': 'No card detected. Please try again.'})

#             # Fetch the customer based on the card number
#             customer = get_object_or_404(Customer, card_number=card_number)

#             # Mark the session as complete and return customer data
#             request.session['nfc_complete'] = True
#             request.session['customer_id'] = customer.card_number
#             return JsonResponse({
#                 'status': 'success',
#                 'customer_id': customer.card_number,
#                 'customer_name': f"{customer.name} {customer.surname}",
#             })

#         except Customer.DoesNotExist:
#             return JsonResponse({'status': 'error', 'message': 'Customer not found.'})
#         except Exception as e:
#             print(f"Error during NFC read: {e}")
#             return JsonResponse({'status': 'error', 'message': 'An error occurred during NFC reading.'})
        
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

# Target App's views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def notify_barcode_read(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            barcode = data.get('barcode')
            # Process the barcode data
            return JsonResponse({'status': 'success', 'message': f'Barcode {barcode} received.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
