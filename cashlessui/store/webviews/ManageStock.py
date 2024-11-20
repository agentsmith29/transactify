from ..models import Customer, Product, StockProductPurchase, StockProductSale
from decimal import Decimal
from django.db.models import Sum

class ManageStock():

    def make_sale(ean : str, quantity: int, sale_price: Decimal, customer: Customer):

        product = Product.objects.get(ean=ean)
        for s in range(quantity):
            StockProductSale.objects.create(product=product,
                                            quantity=1,
                                            sale_price=sale_price,
                                            sold_to=customer)

        quantity_bought = StockProductPurchase.objects.filter(product=product).aggregate(
                quantity=Sum('quantity')
            )['quantity'] or 0
        quantity_sold = StockProductSale.objects.filter(product=product).aggregate(
                quantity=Sum('quantity')
            )['quantity'] or 0
        print(f"quantity_bough: {quantity_bought}, quantity_sold: {quantity_sold}")
        quantity = quantity_bought - quantity_sold

        # Update the stock of the product with the given EAN
        product.stock_quantity = quantity
        product.save()
    
    def make_purchase(ean : str, quantity: int, purchase_price: Decimal):
        # Retrieve the product by EAN
        product = Product.objects.get(ean=ean)

        # Create a new StockProductPurchase record
        StockProductPurchase.objects.create(
            product=product,
            quantity=quantity,
            purchase_price=purchase_price,
            total_cost=purchase_price * quantity
        )

        # Calculate total purchased and sold quantities
        quantity_bought = StockProductPurchase.objects.filter(product=product).aggregate(
            quantity=Sum('quantity')
        )['quantity'] or 0
        quantity_sold = StockProductSale.objects.filter(product=product).aggregate(
            quantity=Sum('quantity')
        )['quantity'] or 0

        # Update stock quantity
        product.stock_quantity = quantity_bought - quantity_sold
        product.save()