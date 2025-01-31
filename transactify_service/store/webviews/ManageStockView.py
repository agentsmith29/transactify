import json
from decimal import Decimal

from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum
from django.db import transaction

from store.helpers.ManageStockHelper import StoreHelper


from ..webmodels.StoreProduct import StoreProduct
from ..webmodels.CustomerPurchase import CustomerPurchase
from ..webmodels.ProductRestock import ProductRestock

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from store import StoreLogsDBHandler
from django.http import JsonResponse
from transactify_service.HttpResponses import HTTPResponses

from transactify_service.settings import CONFIG
import logging


#from ..apps import hwcontroller
@method_decorator(login_required, name='dispatch')
class ManageStockView(View):
    template_name = 'store/stocks.html'
    

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f"{CONFIG.webservice.SERVICE_NAME}.webviews.{self.__class__.__name__}")
        super().__init__(**kwargs)


    def post(self, request):
        try:
            
            # check the header for field cmd
            if 'cmd' in request.headers:
                cmd = request.headers['cmd']
            else:
                cmd = "add"

            data = json.loads(request.body)
            self.logger.debug(f"Post request recieved: {data}")
        
            ean = data.get('product_ean')
            quantity = data.get('quantity')
            purchase_price = data.get('purchase_price') 
            store_equity = bool(data.get('store_equity'))
            with transaction.atomic():
                try:
                    quantity = int(quantity)  # Validate Decimal conversion
                    purchase_price = Decimal(purchase_price)
                except Exception as e:
                    self.logger.error(f"Invalid input for quantity or purchase_price: {e}")
                    return JsonResponse({'success': False, 'message': f"Invalid input for quantity or purchase_price: {e}. Please enter a valid number."}, status=400)
                response, product = StoreHelper.restock_product(ean, quantity, purchase_price, 
                                                                request.user,                                                                
                                                                self.logger, store_equity)
                data, status = response.json_data()
                return JsonResponse(data=data, status=status)
        except Exception as e:
            # -- Comment 3: Catch generic exceptions and log them
            self.logger.error(f"Unexpected error: {e}")
            data, status = HTTPResponses.HTTP_STATUS_PRODUCT_CREATE_FAILED(ean if 'ean' in locals() else "", str(e)).json_data()
            return JsonResponse(data, status=status)

    def get(self, request):
       # websocket.push_cmd_sync()
        
        # Render the template with context
        context = {
            'products': StoreProduct.objects.all(),
            'purchases': CustomerPurchase.objects.all(),
            'restocks': ProductRestock.objects.all(),
            
        }
        return render(request, self.template_name, context)
