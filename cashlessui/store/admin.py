from django.contrib import admin
from .webmodels.StoreProduct import StoreProduct#, StockProductPurchase, StockProductSale, Customer


@admin.register(StoreProduct)
class StoreProductAdmin(admin.ModelAdmin):
    list_display = ('ean', 'name', 'stock_quantity', 'resell_price')
    readonly_fields = ('ean',)


# @admin.register(StockProductPurchase)
# class StockProductPurchaseAdmin(admin.ModelAdmin):
#     list_display = ('product', 'quantity', 'purchase_price', 'total_cost', 'purchase_date')
#     readonly_fields = ('product', 'purchase_date')


# @admin.register(StockProductSale)
# class StockProductSaleAdmin(admin.ModelAdmin):
#     list_display = ('product', 'quantity', 'sale_price', 'sale_date', 'sold_to')


# @admin.register(Customer)
# class CustomerAdmin(admin.ModelAdmin):
#     list_display = ('card_number', 'name', 'surname',
#                     'issued_at', 'balance')
