from django.urls import path
from . import views

urlpatterns = [
    path('add-product/', views.add_new_product, name='add_product'),
    path('add-stock/', views.add_stock, name='add_stock'),
    path('make-sale/', views.make_sale, name='make_sale'),
    path('view-stock/', views.view_stock, name='view_stock'),
    path('customers/', views.add_customer, name='customers'),
    path('financial-summary/', views.view_financial_summary, name='financial_summary'),
]
