from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum
from decimal import Decimal
from ..models import Product, StockProductPurchase, StockProductSale
from .ManageStock import ManageStock


class ViewManageStock(View):
    template_name = 'store/add_stock.html'

    def post(self, request):
        ean = request.POST.get('ean')
        quantity = int(request.POST.get('quantity'))
        purchase_price = Decimal(request.POST.get('purchase_price'))

        try:
           ManageStock.make_purchase(ean, quantity, purchase_price)
        except Product.DoesNotExist:
            return HttpResponse("Error: Product with the given EAN does not exist.", status=404)

        return self.get(request)

    def get(self, request):
        # Render the template with context
        context = {
            'products': Product.objects.all(),
            'sales': StockProductSale.objects.all(),
            'purchases': StockProductPurchase.objects.all()
        }
        return render(request, self.template_name, context)
