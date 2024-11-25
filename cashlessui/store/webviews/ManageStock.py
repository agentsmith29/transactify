from ..webmodels.StoreProduct import StoreProduct
from ..webmodels.CustomerPurchase import CustomerPurchase
from cashlessui.models import Customer
from decimal import Decimal
from django.db.models import Sum

class ManageStock():

    def make_sale(ean : str, quantity: int, sale_price: Decimal, customer: Customer):
        
        # update the balance of the customer by summing all deposits and substracting all buys
        #customer.balance = customer.deposits.aggregate(
        #    total=Sum('amount')
        #)['total'] or 0 - customer.buys.aggregate(
        #    total=Sum('total_cost')
        #)['total'] or 0

        if customer.balance < quantity * sale_price:
            raise ValueError("Insufficient balance")

        product = StoreProduct.objects.get(ean=ean)
        for s in range(quantity):
            CustomerPurchase.objects.create(product=product,
                                            quantity=1,
                                            sale_price=sale_price,
                                            sold_to=customer)

        quantity_bought = CustomerPurchase.objects.filter(product=product).aggregate(
                quantity=Sum('quantity')
            )['quantity'] or 0
        quantity_sold = CustomerPurchase.objects.filter(product=product).aggregate(
                quantity=Sum('quantity')
            )['quantity'] or 0
        print(f"quantity_bough: {quantity_bought}, quantity_sold: {quantity_sold}")
        quantity = quantity_bought - quantity_sold


        # Update the stock of the product with the given EAN
        product.stock_quantity = quantity
        product.save()
    
    def make_purchase(ean : str, quantity: int, purchase_price: Decimal):
        # Retrieve the product by EAN
        product = StoreProduct.objects.get(ean=ean)

        # Create a new StockProductPurchase record
        CustomerPurchase.objects.create(
            product=product,
            quantity=quantity,
            purchase_price=purchase_price,
            total_cost=purchase_price * quantity
        )

        # Calculate total purchased and sold quantities
        quantity_bought = CustomerPurchase.objects.filter(product=product).aggregate(
            quantity=Sum('quantity')
        )['quantity'] or 0
        quantity_sold = CustomerPurchase.objects.filter(product=product).aggregate(
            quantity=Sum('quantity')
        )['quantity'] or 0

        # Update stock quantity
        product.stock_quantity = quantity_bought - quantity_sold
        product.save()