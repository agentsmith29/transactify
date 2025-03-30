from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from store.webmodels.StoreProduct import StoreProduct
from store.webmodels.CustomerPurchase import CustomerPurchase
from django.shortcuts import render

from transactify_service.settings import CONFIG
import logging
import json
import os

from django.conf import settings 
from store.helpers.WebImageDownloader import WebImageDownloader
from store.helpers.ManageStockHelper import StoreHelper


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
        product = get_object_or_404(StoreProduct, ean=ean)
        if product.nutri_score is None or product.nutri_score == "":
            try:
                # Attempt to create the extractor and fetch nutrition facts
                offextractor = OFFExtractor(product)
                offextractor.update_product_async()
            except Exception as e:
                self.logger.error(f"Error during product creation: {e}. Skipping. (You need to manually add the nutrition facts)")

        return product

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

    def post(self, request, ean, *args, **kwargs):
        """
        Handle POST requests to the product detail view.
        """
        try:
            product = get_object_or_404(StoreProduct, ean=ean)
            # check the header for field cmd
            if 'cmd' in request.headers:
                cmd = request.headers['cmd']
            else:
                cmd = "add"

            data = json.loads(request.body)
            self.logger.info(f"Received POST request with command {cmd} for EAN: {product.ean}. Data: {data}")

            if cmd == "update_from_url":
                url = data.get('image_url')
                if not url:
                    return JsonResponse({'message': 'Missing image URL.'}, status=400)
                filename = f"{os.path.abspath(settings.STATIC_ROOT)}/images/products/product_{product.ean}"
                downloader = WebImageDownloader(url, filename)
                filename, static_path = downloader.download()
                product.image_url = static_path
                product.image_source = "url"
                product.save()
                self.logger.info(f"Product image updated for EAN: {product.ean}")
                return JsonResponse({'message': 'Product image updated.'}, status=200)
            elif cmd == "update_from_off":
                offextractor = OFFExtractor(product)
                offextractor.update_product_async()
                self.logger.info(f"Product updated from OFF for EAN: {product.ean}")
                return JsonResponse({'message': 'Product updated from OFF.'}, status=200)
            elif cmd == "update_product":
                try:
                    product_name = data.get('product_name', None)
                    resell_price = data.get('resell_price', None)
                    discount = data.get('discount', None)
                    nutri_score = data.get('nutri_score', None)
                    energy_kcal = data.get('energy_kcal', None)
                    energy_kj = data.get('energy_kj', None)
                    fat = data.get('fat', None)
                    carbohydrates = data.get('carbohydrates', None)
                    sugar = data.get('sugar', None)
                    fiber = data.get('fiber', None)
                    proteins = data.get('proteins', None)
                    salt = data.get('salt', None)
                except Exception as e:
                    self.logger.error(f"Error parsing product data: {e}")
                    return JsonResponse({'message': 'Invalid product data.'}, status=400)
                
                response, product = StoreHelper.update_product_details(
                    product,
                    product_name=product_name,
                    resell_price=resell_price,
                    discount=discount, 
                    nutri_score=nutri_score, 
                    energy_kcal=energy_kcal, 
                    energy_kj=energy_kj, 
                    fat=fat, 
                    carbohydrates=carbohydrates, 
                    sugar=sugar, 
                    fiber=fiber, 
                    proteins=proteins, 
                    salt=salt, 
                    logger=self.logger)
                self.logger.info(f"Product updated for EAN: {product.ean}")
                data, status = response.json_data()
                return JsonResponse(data=data, status=status)
            
            else:
                return JsonResponse({'message': f'Invalid command {cmd}'}, status=400)

        except Exception as e:
            self.logger.error(f"Error parsing POST request: {e}")
            return JsonResponse({'message': 'Invalid request.'}, status=400)
       