from django.urls import path
from . import views
from .views import PresentCardView#, #CheckNFCStatus, NFCReadView, UpdateCustomerBalance
from .webviews.ManageProductView import ManageProductsView
from .webviews.ManageStockView import ManageStockView
from .webviews.ManageCustomersView import ManageCustomersView
from .webviews.SingleCustomerView import SingleCustomerView
from .webviews.MakePurchaseView import MakePurchaseView
from .webviews.StoreLogListView import StoreLogListView



urlpatterns = [
    path('customers/', ManageCustomersView.as_view(), name='customers'),
    path('manage-products/', ManageProductsView.as_view(), name='manage_products'),
    path('manage-stock/', ManageStockView.as_view(), name='manage_stock'),

    path('customer/<str:card_number>/', SingleCustomerView.as_view(), name='customer_detail'),
    #path('customer/<str:card_number>/update_balance/', UpdateCustomerBalance.as_view(), name='customer_update_balance'),

    path('make-sale/', MakePurchaseView.as_view(),  name='make_sale'),
    #path('view-stock/', views.view_stock, name='view_stock'),
    
    path('present_card/', PresentCardView.as_view(), name='present_card'),
    #path('nfc_read/', NFCReadView.as_view(), name='nfc_read'),
    #path('customer/', ViewSingleCustomer.as_view(), name='customer'),

    #path('financial-summary/', views.view_financial_summary, name='financial_summary'),
    path('logs/', StoreLogListView.as_view(), name='store_logs'),
]
