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
from django.http import HttpResponse

from decimal import Decimal
from .ManageStockHelper import ManageStockHelper
from ..webmodels.StoreProduct import StoreProduct
from ..webmodels.CustomerPurchase import CustomerPurchase

from ..apps import hwcontroller

class MakePurchaseView(View):
    template_name = 'store/make_sale.html'
    def __init__(self):
        pass
                      

    def get(self, request):
        """Handle GET requests to display all products."""
        store_products = StoreProduct.objects.all()
        return render(request, self.template_name, {'products': store_products})

    def post(self, request):
        #     if request.method == 'POST':
        ean = request.POST.get('ean')
        quantity = int(request.POST.get('quantity'))
        sale_price = Decimal(request.POST.get('sale_price'))
        customer = request.POST.get('customer')
        try:
             ManageStockHelper.make_sale(ean, quantity, sale_price, customer)
        except StoreProduct.DoesNotExist:
             return HttpResponse("Error: Product with the given EAN does not exist.")
        
        return render(request, 'store/make_sale.html', {
            'products': StoreProduct.objects.all()
        })
