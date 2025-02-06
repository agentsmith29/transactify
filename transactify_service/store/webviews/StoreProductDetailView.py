from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from store.webmodels.StoreProduct import StoreProduct
from store.webmodels.CustomerPurchase import CustomerPurchase
from django.shortcuts import render

from transactify_service.settings import CONFIG
import logging

from store.helpers.OFFExtractor import OFFExtractor

class StoreProductDetailView(DetailView):
    model = StoreProduct
    template_name = "store/product_details.html"
    context_object_name = "product"

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f"{CONFIG.webservice.SERVICE_NAME}.webviews.{self.__class__.__name__}")
        super().__init__(**kwargs)

    def get_object(self, ean):
        """
        Override the get_object method to fetch the product by its ID or slug.
        """
        # Fecth the nutrion facts for the product
        # Initialize offextractor to None
        offextractor = None
        nutri_facts = {}

        try:
            # Attempt to create the extractor and fetch nutrition facts
            offextractor = OFFExtractor(ean)
            nutri_facts = offextractor.extract()
        except Exception as e:
            self.logger .error(f"Error during product creation: {e}. Skipping. (You need to manually add the nutrition facts)")
        
        try:
            product = StoreProduct.objects.get(ean=ean)
    
            # Assign nutrition facts if available
            if nutri_facts:
                product.nutri_score = nutri_facts.get("Nutri-Score")
                product.energy_kcal = nutri_facts.get("Energy (kcal)")
                product.energy_kj = nutri_facts.get("Energy (kJ)")
                product.fat = nutri_facts.get("Fat")
                product.carbohydrates = nutri_facts.get("Carbohydrates")
                product.sugar = nutri_facts.get("Sugar")
                product.fiber = nutri_facts.get("Fiber")
                product.proteins = nutri_facts.get("Proteins")
                product.salt = nutri_facts.get("Salt")
                product.image_url = nutri_facts.get("Image URL")
            product.save()
        except Exception as e:
            self.logger .error(f"Error during product creation: {e}")

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
