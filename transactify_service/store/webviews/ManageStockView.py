import json
from decimal import Decimal

from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum

from store.helpers.ManageStockHelper import StoreHelper


from ..webmodels.StoreProduct import StoreProduct
from ..webmodels.CustomerPurchase import CustomerPurchase
from ..webmodels.ProductRestock import ProductRestock

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from store import StoreLogsDBHandler

#from ..apps import hwcontroller
@method_decorator(login_required, name='dispatch')
class ManageStockView(View):
    template_name = 'store/add_stock.html'

    def __init__(self):
        super().__init__()
        self.logger = StoreLogsDBHandler.setup_custom_logging('ManageProductsView')


    def post(self, request):
        ean = request.POST.get('ean')
        quantity = int(request.POST.get('quantity'))
        purchase_price = Decimal(request.POST.get('purchase_price'))

        try:
           response, product = StoreHelper.restock_product(ean, quantity, purchase_price, self.logger )
           if response.status_code != 200:
               return response
        except StoreProduct.DoesNotExist:
            return HttpResponse("Error: Product with the given EAN does not exist.", status=404)

        return self.get(request)

    def get(self, request):
        # Render the template with context
        context = {
            'products': StoreProduct.objects.all(),
            'purchases': CustomerPurchase.objects.all(),
            'restocks': ProductRestock.objects.all()
        }
        return render(request, self.template_name, context)
