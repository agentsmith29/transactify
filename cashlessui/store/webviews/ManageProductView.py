from django.shortcuts import render, redirect
from django.views import View
from django.shortcuts import render
from ..webmodels.StoreProduct import StoreProduct
from decimal import Decimal
from django.db.models import Sum, F
import os

class ManageProductsView(View):
    template_name = 'store/manage_products.html'

    def get(self, request):
        """Handle GET requests to display all products."""
        products = StoreProduct.objects.all()
        return render(request, self.template_name, {'products': products})

    def post(self, request):
        """Handle POST requests for adding or editing products."""

        # run ls app/static/assets/dist/js/bootstrap.bundle.min.js
        import os
  
        #             
        ean = request.POST.get('ean')
        name = request.POST.get('name')
        resell_price = request.POST.get('resellprice')
        print(f"********* request.POST: {request.POST}\n\n\n")
        if 'delete_ean' in request.POST:
            ean = request.POST.get('delete_ean')
            print(f"********* Trying to delete product with EAN: {ean}\n\n\n")
            # Delete the product with the given EAN
            StoreProduct.objects.filter(ean=ean).delete()
            return redirect('manage_products')
       

        # Create a new product
        product, inst = StoreProduct.objects.get_or_create(
            ean=ean
        )
        product.name = name
        product.resell_price = resell_price
        product.save()

        # Redirect to avoid resubmission issues
        return redirect('manage-products')

