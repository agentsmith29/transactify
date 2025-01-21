import json

from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from store.webmodels.Customer import Customer
from store.helpers.ManageStockHelper import StoreHelper

from ..webmodels.CustomerDeposit import CustomerDeposit
from ..webmodels.StoreProduct import StoreProduct
from ..webmodels.CustomerPurchase import CustomerPurchase

from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from transactify_service.settings import CONFIG
import logging

#from ..apps import hwcontroller
@method_decorator(login_required, name='dispatch')
class MakePurchaseView(View):
    template_name = 'store/make_sale.html'

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f"{CONFIG.webservice.SERVICE_NAME}.webviews.{self.__class__.__name__}")
        super().__init__(**kwargs)

                    
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
             StoreHelper.customer_purchase(ean, quantity, sale_price, customer, self.logger)
        except StoreProduct.DoesNotExist:
             return HttpResponse("Error: Product with the given EAN does not exist.")
        
        return render(request, 'store/make_sale.html', {
            'products': StoreProduct.objects.all()
        })
