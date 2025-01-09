from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from store.webmodels.StoreProduct import StoreProduct
from store.webmodels.CustomerPurchase import CustomerPurchase
from django.shortcuts import render

class StoreProductDetailView(DetailView):
    model = StoreProduct
    template_name = "store/product_details.html"
    context_object_name = "product"

    def get_object(self, ean):
        """
        Override the get_object method to fetch the product by its ID or slug.
        """
        return get_object_or_404(StoreProduct, ean=ean)

    def get_context_data(self, ean, **kwargs):
        """
        Add additional context data for the product detail view.
        """
        
        #num_of_orders = CustomerPurchase.objects.filter(product=self.get_object()).count()
        #revenue = sum([purchase.revenue for purchase in CustomerPurchase.objects.filter(product=self.get_object())])
        # context = super().get_context_data(**kwargs)
        product = self.get_object(ean)
        max_stock = 10
        stock_percentage = (product.stock_quantity / max_stock) * 100

        context = {
            "product": product,
            'in_stock': product.stock_quantity > 0,
            "stock_percentage":  stock_percentage,
        }

        return context
    
    def get(self, request, ean, *args, **kwargs):
        """
        Handle GET requests to the product detail view.
        """
        return render(request, self.template_name, self.get_context_data(ean))
