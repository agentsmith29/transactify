from rest_framework import serializers
from store.webmodels.StoreProduct import StoreProduct

class StoreProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = StoreProduct
        fields = ['ean', 'name', 'stock_quantity', 'discount', 'resell_price', 'final_price']

