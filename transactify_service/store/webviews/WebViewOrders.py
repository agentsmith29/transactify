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
from transactify_service.settings import CONFIG
import logging
import traceback

import json

@method_decorator(login_required, name='dispatch')
class WebViewOrders(View):
    template_name = 'store/orders.html'

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f"{CONFIG.webservice.SERVICE_NAME}.webviews.{self.__class__.__name__}")
        super().__init__(**kwargs)

    def get(self, request):
        context = {'purchases_list': CustomerPurchase.objects.filter().all().order_by('-purchase_date'),
                   }
        return render(request, self.template_name, context)

    def post(self, request):
        pass