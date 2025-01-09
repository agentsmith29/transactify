from decimal import Decimal
from django.shortcuts import render
from django.views import View
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from store.webmodels.StoreProduct import StoreProduct
from store.helpers.ManageStockHelper import StoreHelper
from transactify_service.HttpResponses import HTTPResponses
from store.webmodels.Customer import Customer
from store.webmodels.CustomerPurchase import CustomerPurchase

from store import StoreLogsDBHandler
import traceback

import json

@method_decorator(login_required, name='dispatch')
class WebViewOrders(View):
    template_name = 'store/orders.html'

    def get(self, request):
        context = {'purchases_list': CustomerPurchase.objects.filter().all(),
        
                   }
        return render(request, self.template_name, context)

    def post(self, request):
        pass