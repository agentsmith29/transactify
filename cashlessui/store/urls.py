from django.urls import path
from . import views
from .views import ViewCustomers, ViewSingleCustomer, PresentCardView, CheckNFCStatus, NFCReadView, UpdateCustomerBalance
from .webviews.ManageProductView import ManageProductsView
from .webviews.ViewManageStock import ViewManageStock

urlpatterns = [
    path('manage-products/', ManageProductsView.as_view(), name='manage_products'),
    path('manage-stock/',ViewManageStock.as_view(), name='manage_stock'),
    path('make-sale/', views.make_sale, name='make_sale'),
    path('view-stock/', views.view_stock, name='view_stock'),
    
    path('present_card/', PresentCardView.as_view(), name='present_card'),
    path('nfc_read/', NFCReadView.as_view(), name='nfc_read'),
    #path('customer/', ViewSingleCustomer.as_view(), name='customer'),

    path('customers/', ViewCustomers.as_view(), name='customers'),
    path('customer/<str:card_number>/', ViewSingleCustomer.as_view(), name='customer_detail'),
    path('customer/<str:card_number>/update_balance/', UpdateCustomerBalance.as_view(), name='customer_update_balance'),

    path('financial-summary/', views.view_financial_summary, name='financial_summary'),
]
