from ..webmodels.StoreProduct import StoreProduct
from ..webmodels.CustomerPurchase import CustomerPurchase
from ..webmodels.CustomerDeposit import CustomerDeposit
from ..webmodels.CustomerBalance import CustomerBalance

from ..webmodels.ProductRestock import ProductRestock

from ..webviews.ManageCustomerHelper import ManageCustomerHelper

from cashlessui.models import Customer
from decimal import Decimal
from django.db.models import Sum

import logging

class ManageStockHelper():

    def get_stock_quantity(product: StoreProduct) -> int:
               # Get the total quantity of the product bought and sold, to calulate how many are left
        quantity_bought = ProductRestock.get_all_restocks_aggregated(product=product) or 0
        quantity_sold = CustomerPurchase.get_all_purchases_aggregated(product=product) or 0
        print(f"quantity_bough: {quantity_bought}, quantity_sold: {quantity_sold}")
        return quantity_bought - quantity_sold
 
        
    def customer_purchase(ean : str, quantity: int, purchase_price: Decimal, card_number: str):

        logger = logging.getLogger('Purchase')
        logger.info(f"[PURCHASE] Initiating purchase of product with EAN {ean}"
                    f"Quantity: {quantity}, Purchase Price: {purchase_price}, Card Number: {card_number}")
        # First we need to get the customer balance and the number of products to make a check if we can even sell 
        # or make a purchase
        try:
            customer = Customer.objects.get(card_number=card_number)
        except Customer.DoesNotExist:
            logger.error(f"[PURCHASE] Purchase failed due to customer not found with card number: {card_number}")
            return -1, None, None, None, None
        
        balance = customer.get_balance(CustomerBalance)
        product = StoreProduct.objects.get(ean=ean)

        # Check if the customer has enough balance to make the purchase
        if balance < quantity * purchase_price:
            logger.error(f"[PURCHASE] Purchase failed due to insufficient balance (is: {balance}, req: {quantity} x {purchase_price} = {quantity * purchase_price}) for customer {customer}")
            return -2, None, None, None, None
        
        left_in_stock = ManageStockHelper.get_stock_quantity(product)
        # Check if the product is in stock
        if left_in_stock <= 0:
            logger.error(f"[PURCHASE] Purchase failed due to insufficient stock for product {product}")
            return -3, None, None, None, None
        
        try:
            customer, customer_balance, purchase_entry = ManageCustomerHelper.customer_add_purchase(
                customer=customer, 
                amount=purchase_price,
                quantity=quantity, 
                product=product, 
                )
        except Exception as e:
            logger.error(f"[PURCHASE] Purchase failed due to an error: {e}")
            return -5, None, None, None, None
        
        try:
            # Update the stock of the product with the given EAN
            product.stock_quantity = ManageStockHelper.get_stock_quantity(product)
            # Save the changes, and log the successful purchase
            product.save()
            # 
            if product.stock_quantity <= 0:
                logger.warning(f"[PURCHASE] Product {product} is out of stock now.")

            
        except Exception as e:
            logger.error(f"[PURCHASE] Purchase failed due to an error: {e}")
            return -5, None, None, None, None
        
        logger.info(f"[PURCHASE] Purchase successful. New stock quantity: {product.stock_quantity}")
        return 0, customer, customer_balance, product, purchase_entry
    
    def get_or_create_product(ean: str, name: str, resell_price: Decimal):
        # Create a new StoreProduct record
        logger = logging.getLogger('store')
        logger.info(f"[CREATE PRODUCT] Creating product with EAN {ean}, Name: {name}, Resell Price: {resell_price}")
        product, inst = StoreProduct.objects.get_or_create(
            ean=ean
        )
        product.name = name
        product.resell_price = resell_price
        product.save()
        logger.info(f"[CREATE PRODUCT] Product created: {product}")
        return product, inst

    def restock_product(ean : str, quantity: int, purchase_price: Decimal):
        # Retrieve the product by EAN
        logger = logging.getLogger('store')
        logger.info(f"[Restock] Initiating restock of product with EAN {ean} Quantity: {quantity}, Purchase Price: {purchase_price}")
        try:
            product = StoreProduct.objects.get(ean=ean)
        except StoreProduct.DoesNotExist:
            logger.error(f"[Restock] Product with EAN {ean} does not exist.")
            return -1, None

        # Create a new StockProductPurchase record
        product_restock =  ProductRestock.objects.create(
            product=product,
            quantity=quantity,
            purchase_price=purchase_price,
            total_cost=purchase_price * quantity
        )
        # Update stock quantity
        product.stock_quantity = ManageStockHelper.get_stock_quantity(product)
        product.save()
        return 0, product, product_restock