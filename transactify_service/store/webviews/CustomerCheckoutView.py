import json
import logging
import traceback
from decimal import Decimal, ROUND_HALF_UP

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin

from store.webmodels.Customer import Customer
from store.webmodels.StoreProduct import StoreProduct
from store.webmodels.CustomerPurchase import CustomerPurchase
from store.helpers.ManageStockHelper import StoreHelper
from transactify_service.settings import CONFIG

class CustomerCheckoutView(View, LoginRequiredMixin):
    template_name = 'store/checkout.html'

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f"{CONFIG.webservice.SERVICE_NAME}.webviews.{self.__class__.__name__}")
        super().__init__(**kwargs)

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, card_number=None):
        """
        Handle GET requests to display available products and customer checkout details.
        """
        products = StoreProduct.objects.filter(stock_quantity__gt=0)  # Only show in-stock products

        try:
            customer = Customer.objects.get(card_number=card_number)
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'Customer profile not found'}, status=404)

        return render(request, self.template_name, {
            'auth_user': request.user,
            'customer': customer,
            'products': products,
        })

    @transaction.atomic
    def post(self, request, card_number=None):
        """
        Handle POST requests to process a checkout transaction.
        """
        try:
            data = json.loads(request.body)
            items = data.get("items", [])

            if not card_number or not items:
                return JsonResponse({'error': 'Invalid request. No items provided.'}, status=400)
            # Fetch the customer
            customer = get_object_or_404(Customer, card_number=card_number)

            for item in items:
                ean = item.get("ean")
                quantity = int(item.get("quantity"))
                
                response, _ = StoreHelper.customer_purchase(ean=ean, quantity=quantity, card_number=card_number, logger=self.logger, prepaid = True)
                data, status = response.json_data()
                return JsonResponse(data=data, status=status)
            return status

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            self.logger.error(f"Checkout error: {e}\nTraceback:\n{traceback.format_exc()}")
            return JsonResponse({'error': 'An error occurred during checkout'}, status=500)
