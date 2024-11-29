from ..webmodels.StoreProduct import StoreProduct
from ..webmodels.CustomerPurchase import CustomerPurchase
from ..webmodels.CustomerBalance import CustomerBalance

from cashlessui.models import Customer
from decimal import Decimal
from django.db.models import Sum

class ManageStockHelper():

    def make_sale(ean : str, quantity: int, purchase_price: Decimal, card_number: str):
        
        customer = Customer.objects.get(card_number=card_number)
        balance = customer.get_balance(CustomerBalance)
        if balance < quantity * purchase_price:
            return -1
        else:
            balance = customer.decrement_balance(CustomerBalance, quantity * purchase_price)

        product = StoreProduct.objects.get(ean=ean)
        for s in range(quantity):
            # Always create a new CustomerPurchase record
            CustomerPurchase.objects.create(product=product, quantity=1,
                                            purchase_price=purchase_price,
                                            customer=customer, customer_balance=balance,
                                            )
            

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

        balance.save()
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