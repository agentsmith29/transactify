from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum
from decimal import Decimal
from ..webmodels.StoreProduct import StoreProduct
from ..webmodels.CustomerPurchase import CustomerPurchase
from ..webmodels.ProductRestock import ProductRestock
from .ManageStock import ManageStock


class ViewManageStock(View):
    template_name = 'store/add_stock.html'

    def post(self, request):
        ean = request.POST.get('ean')
        quantity = int(request.POST.get('quantity'))
        purchase_price = Decimal(request.POST.get('purchase_price'))

        try:
           ManageStock.make_purchase(ean, quantity, purchase_price)
        except StoreProduct.DoesNotExist:
            return HttpResponse("Error: Product with the given EAN does not exist.", status=404)

        return self.get(request)

    def get(self, request):
        # Render the template with context
        context = {
            'products': StoreProduct.objects.all(),
            'sales': CustomerPurchase.objects.all(),
            # TODO: rename 'purchases' to 'restocks'
            'purchases': ProductRestock.objects.all()
        }
        return render(request, self.template_name, context)
