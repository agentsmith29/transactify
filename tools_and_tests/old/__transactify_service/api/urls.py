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


router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customers')
router.register(r'products', ProductViewSet, basename='products')


urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    # API Calls for the customers model
    #path('customers', CustomerList.as_view()),
    #path('customers/<str:pk>/', CustomerDetail.as_view()),
    # API Calls for the products model
    path('', include(router.urls)),
]

#urlpatterns = format_suffix_patterns(urlpatterns)

# APIs
    