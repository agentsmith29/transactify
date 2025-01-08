from store.helpers.ManageStockHelper import StoreHelper
import logging

from django.contrib.auth.models import User
from store.webmodels.Customer import Customer
from store.webmodels.StoreProduct import StoreProduct
from store.webmodels.ProductRestock import ProductRestock
from store.webmodels.CustomerDeposit import CustomerDeposit
from store.webmodels.CustomerPurchase import CustomerPurchase

import random
from datetime import datetime, timedelta

logger = logging.getLogger('Mocker')
def generate_random_date(time_delta=30):
    # Calculate the datetime range
    now = datetime.now()
    start_date = now - timedelta(days=time_delta)
    
    # Generate a random date within the last 30 days
    random_date = start_date + timedelta(seconds=random.randint(0, int((now - start_date).total_seconds())))
    
    # Set the random time to be within the range of 9 AM to 5 PM
    random_hour = random.randint(9, 16)  # 16 ensures the latest hour is 5 PM
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)
    
    # Combine the date with the random time
    return random_date.replace(hour=random_hour, minute=random_minute, second=random_second)

def generate_random_number(start=10.0, end=100.0):
    return round(random.uniform(start, end), 2)

def generate_random_numeric_string(digits=16):
    return ''.join([str(random.randint(0, 9)) for _ in range(digits)])

# ============= Mocking the store content =============
def delete_mocked_customers(username):
    
        # delete the user if it exists
        try:
            user = User.objects.get(username=username)
        except Exception as e:
            logger.error(f"Failed to get user {username}: {e}")
        
        try:
            customer = Customer.objects.get(user=user)  
        except Exception as e:
            logger.error(f"Failed to get customer {username}: {e}")
        
        try:
            customer.delete()
        except Exception as e:
            logger.error(f"Failed to delete customer {username}: {e}")

        try:
            user.delete()
        except Exception as e:
            logger.error(f"Failed to delete user {username}: {e}")
        delete_mocked_customer_deposits(username)

def mock_store_customers():
    # create a list of customers
    #delete user{i}
    for i in range(1, 10):
        username=f"user{i}"
        delete_mocked_customers(username)
        # username: str, first_name: str, last_name: str, email: str, balance: Decimal, card_number: str, logger: logging.Logger
        logger_mock_store_customers = logging.getLogger('CreateNewCustomer')
        rsp, customer = StoreHelper.create_new_customer(username=username, 
                                        first_name=f"first{i}", last_name=f"last{i}", 
                                        email=f"last{i}.first{i}@user{i}.com", 
                                        balance=generate_random_number(10, 150), 
                                        card_number=f"{i}_{generate_random_numeric_string(16)}", 
                                        logger=logger_mock_store_customers)
        # generate a random date between now and 30 days ago, but only between 9am and 5pm
        customer.issued_at = generate_random_date(30)
        customer.save()
        # Create some products

def delete_mocked_customer_deposits(username):
    try:
        user = User.objects.get(username=username)
    except Exception as e:
        logger.error(f"Failed to get user {username}: {e}")
    
    try:
        customer = Customer.objects.get(user=user)
    except Exception as e:
        logger.error(f"Failed to get customer {username}: {e}")
    
    try:
        deposits = CustomerDeposit.objects.filter(customer=customer)
    except Exception as e:
        logger.error(f"Failed to get deposits for customer {username}: {e}")
    
    try:
        deposits.delete()
    except Exception as e:
        logger.error(f"Failed to delete deposits for customer {username}: {e}")

def mock_customer_deposits():
    for i in range(1, 10):
        username=f"user{i}"
        #delete_mocked_customer_deposits(username)
        try:
            user = User.objects.get(username=username)
        except Exception as e:
            logger.error(f"Failed to get user {username}: {e}")
            continue
        
        try:
            customer = Customer.objects.get(user=user)
        except Exception as e:
            logger.error(f"Failed to get customer user{i}: {e}")
            continue

        logger_mock_customer_deposits = logging.getLogger('AddCustomerDeposit')
        rsp, customer_deposit = StoreHelper.customer_add_deposit(customer, generate_random_number(10, 150), logger_mock_customer_deposits)
        customer_deposit.deposit_date = generate_random_date(30)
        customer_deposit.save()


# =====================================================================================================================
def delete_mocked_products(name):
    try:
        product = StoreProduct.objects.get(name=name)
    except Exception as e:
        logger.error(f"Failed to get product {name}: {e}")
    
    try:
        product.delete()
    except Exception as e:
        logger.error(f"Failed to delete product {name}: {e}")

def mock_store_products():
    for i in range(0, 16):
        name = f"test_product{i}"
        delete_mocked_products(name)
        logger_mock_store_products = logging.getLogger('CreateNewProduct')
        rsp, product = StoreHelper.get_or_create_product(
            ean=f"{i}_f{generate_random_numeric_string(8)}", 
            name=f"test_product{i}", 
            resell_price=generate_random_number(1, 15), 
            discount=generate_random_number(1, 10)/100,
            logger=logger_mock_store_products)

# =====================================================================================================================
def delete_mocked_restocks(product_name):
    try:
        product = StoreProduct.objects.get(name=product_name)
    except Exception as e:
        logger.error(f"Failed to get product {product_name}: {e}")
    
    try:
        restocks = ProductRestock.objects.filter(product=product)
    except Exception as e:
        logger.error(f"Failed to get restock for product {product_name}: {e}")
    
    try:
        restocks.delete()
    except Exception as e:
        logger.error(f"Failed to delete restock for product {product_name}: {e}")

def mock_restocks():
    for i in range(0, 16):
        try:
            product = StoreProduct.objects.get(name=f"test_product{i}")
        except Exception as e:
            logger.error(f"Failed to get user user{i}: {e}")
            continue
        
        logger_mock_restocks = logging.getLogger('RestockProduct')
        rsp, product_restock = StoreHelper.restock_product(
            ean=product.ean, 
            quantity=random.randint(1, 10), 
            purchase_price=generate_random_number(1, 15), 
            logger=logger_mock_restocks)
        product_restock.restocked_at = generate_random_date(30)
        product_restock.save()

def delete_mocked_purchases(username):
    try:
        user = User.objects.get(username=username)
    except Exception as e:
        logger.error(f"Failed to get user {username}: {e}")
    
    try:
        customer = Customer.objects.get(user=user)
    except Exception as e:
        logger.error(f"Failed to get customer {username}: {e}")
    
    try:
        purchases = CustomerPurchase.objects.filter(customer=customer)
    except Exception as e:
        logger.error(f"Failed to get purchases for customer {username}: {e}")
    
    try:
        purchases.delete()
    except Exception as e:
        logger.error(f"Failed to delete purchases for customer {username}: {e}")

def mock_purchases():
    logger.info("Mocking purchases\n\n\n\n")
    for i in range(1, 10):
        username=f"user{i}"
        try:
            user = User.objects.get(username=username)
        except Exception as e:
            logger.error(f"Failed to get user user{i}: {e}")
            continue
        
        try:
            customer = Customer.objects.get(user=user)
        except Exception as e:
            logger.error(f"Failed to get customer user{i}: {e}")
            continue
        
        try:
            product = StoreProduct.objects.get(name=f"test_product{i}")
        except Exception as e:
            logger.error(f"Failed to get product test_product{i}: {e}")
            continue
        
        # check how many products are available
        if product.stock_quantity == 0:
            continue
        logger_mock_purchases = logging.getLogger('CustomerPurchase')
       # def customer_purchase(ean: str, quantity: int, card_number: str, logger: logging.Logger) -> tuple[Response, Customer]:
        rsp, customer_purchase = StoreHelper.customer_purchase(
            product.ean, random.randint(1, product.stock_quantity), customer.card_number, 
            logger_mock_purchases)
        customer_purchase.purchase_date = generate_random_date(30)
        customer_purchase.save()