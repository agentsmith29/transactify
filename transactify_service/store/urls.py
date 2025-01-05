from django.urls import path
from . import views
#from .views import PresentCardView#, #CheckNFCStatus, NFCReadView, UpdateCustomerBalance

from django.urls import include

from .webviews.ManageProductView import ManageProductsView
from .webviews.ManageStockView import ManageStockView
from .webviews.ManageCustomersView import ManageCustomersView
from .webviews.SingleCustomerView import SingleCustomerView
from .webviews.MakePurchaseView import MakePurchaseView
from .webviews.StoreLogListView import StoreLogListView
from .webviews.ViewFinancialSummary import ViewFinancialSummary

from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

from django.contrib.auth.views import LoginView, LogoutView
from .views import dashboard


urlpatterns = [
    path('', dashboard, name='dashboard'),
    #path(f'{settings.STORE_NAME}/dashboard/', dashboard, name='dashboard'),
    
    path('customers/', ManageCustomersView.as_view(), name='customers'),
    path('manage-products/', ManageProductsView.as_view(), name='manage_products'),
    path('manage-stock/', ManageStockView.as_view(), name='manage_stock'),

    path('customer/<str:card_number>/', SingleCustomerView.as_view(), name='customer_detail'),
    path('make-sale/', MakePurchaseView.as_view(),  name='make_sale'),
    path('financial-summary/', ViewFinancialSummary.as_view(), name='financial_summary'),
    path('logs/', StoreLogListView.as_view(), name='logs'),
]