from django.db import models
from store.webmodels.StoreProduct import StoreProduct
from django.contrib.auth.models import User

class ProductRatings(models.Model):
    product = models.ForeignKey(StoreProduct, 
                                # delete entry only, not the product
                                on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    review = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

