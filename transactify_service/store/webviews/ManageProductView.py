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

from store import StoreLogsDBHandler
import traceback

import json

from transactify_service.settings import CONFIG
import logging

@method_decorator(login_required, name='dispatch')
class ManageProductsView(View):
    template_name = 'store/products.html'

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f"{CONFIG.webservice.SERVICE_NAME}.webviews.{self.__class__.__name__}")
        super().__init__(**kwargs)



    def get(self, request):
        """Handle GET requests to display all products."""
        try:
            products = list(StoreProduct.objects.values())  # Convert QuerySet to a list of dictionaries
            return render(request, self.template_name, {'products': products})
        except Exception as e:
            self.logger.error(f"Error fetching products: {e}")
            traceback.print_exc()
            data, status = HTTPResponses.HTTP_STATUS_PRODUCT_CREATE_FAILED("", str(e)).json_data()
            return JsonResponse(data, status=status)

    def post(self, request):
        """Handle POST requests for adding or editing products."""
        try:
            
            # check the header for field cmd
            if 'cmd' in request.headers:
                cmd = request.headers['cmd']
            else:
                cmd = "add"

            data = json.loads(request.body)
            self.logger.debug(f"Post request recieved: {data}")
            
            ean = data.get('product_ean')

            # Handle delete operation
            if cmd == "delete":
                self.logger.warning(f"Trying to delete product with EAN: {ean}")
                deleted_count, _ = StoreProduct.objects.filter(ean=ean).delete()
                if deleted_count > 0:
                    return JsonResponse({'success': True, 'message': f"Product with EAN {ean} successfully deleted."}, status=200)
                else:
                    return JsonResponse({'success': False, 'message': f"Product with EAN {ean} not found."}, status=404)

            name = data.get('product_name')
            resell_price = data.get('resell_price')
            discount = data.get('discount')

            # -- Comment 1: Validate input data
            if not ean or not name or not resell_price:
                self.logger.error("Missing required fields for product creation.")
                return JsonResponse({'success': False, 'message': "Missing required fields."}, status=400)
            # -- End 1


            # -- Comment 2: Wrap operations in an atomic transaction
            with transaction.atomic():
                try:
                    resell_price = Decimal(resell_price)  # Validate Decimal conversion
                    discount = Decimal(data.get('discount'))
                except Exception as e:
                    self.logger.error(f"Invalid input for resell price: {e}")
                    return JsonResponse({'success': False, 'message': "Invalid resell price. Please enter a valid number."}, status=400)

                response, product = StoreHelper.get_or_create_product(ean, name, resell_price, discount, self.logger)
                data, status = response.json_data()
                return JsonResponse(data=data, status=status)
            
        except Exception as e:
            # -- Comment 3: Catch generic exceptions and log them
            self.logger.error(f"Unexpected error: {e}")
            data, status = HTTPResponses.HTTP_STATUS_PRODUCT_CREATE_FAILED(ean if 'ean' in locals() else "", str(e)).json_data()
            return JsonResponse(data, status=status)
            # -- End 3
