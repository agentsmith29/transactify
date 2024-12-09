from django.urls import path, include
from . import views
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
# for the API
from rest_framework import serializers
#from .webAPI.Customers import CustomerList, CustomerDetail
from .webAPI.Products import ProductViewSet
from .webAPI.Customers import CustomerViewSet   

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter

from .webAPI.CustomerPurchaseAPIView import CustomerPurchaseAPIView


router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customers')
router.register(r'products', ProductViewSet, basename='products')


urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('', include(router.urls)),
    # custom API calls
    path('purchase/', CustomerPurchaseAPIView.as_view(), name='customer_purchase'),
]

#urlpatterns = format_suffix_patterns(urlpatterns)

# APIs
    