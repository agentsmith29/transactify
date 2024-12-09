from rest_framework import serializers
from store.webmodels.StoreProduct import StoreProduct

class StoreProductSerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField()  # Custom field for final price

    class Meta:
        model = StoreProduct
        fields = ['ean', 'name', 'stock_quantity', 'discount', 'resell_price', 'final_price']

    def get_final_price(self, obj: StoreProduct):
        """Retrieve the final price of the product after applying discount."""
        return obj.get_final_price()  # Use the model's method to compute the final price
