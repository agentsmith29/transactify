from store.helpers.ManageStockHelper import StoreHelper
import logging

from django.contrib.auth.models import User
from store.webmodels.Customer import Customer
from store.webmodels.StoreProduct import StoreProduct

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

def mock_store_content():
    # create a list of customers
    #delete user{i}
    for i in range(1, 10):
        # delete the user if it exists
        try:
            user = User.objects.get(username=f"user{i}")
        except Exception as e:
            logger.error(f"Failed to get user user{i}: {e}")
        
        try:
            customer = Customer.objects.get(user=user)  
        except Exception as e:
            logger.error(f"Failed to get customer user{i}: {e}")
        
        try:
            customer.delete()
        except Exception as e:
            logger.error(f"Failed to delete customer user{i}: {e}")

        try:
            user.delete()
        except Exception as e:
            logger.error(f"Failed to delete user user{i}: {e}")
        
        
        # username: str, first_name: str, last_name: str, email: str, balance: Decimal, card_number: str, logger: logging.Logger
        rsp, customer = StoreHelper.create_new_customer(username=f"user{i}", 
                                        first_name=f"first{i}", last_name=f"last{i}", 
                                        email=f"last{i}.first{i}@user{i}.com", 
                                        balance=generate_random_number(10, 150), card_number=f"{i}_{generate_random_numeric_string(16)}", logger=logger)
        # generate a random date between now and 30 days ago, but only between 9am and 5pm
        customer.issued_at = generate_random_date(30)
        customer.save()
        # Create some products

    for i in range(0, 16):
        try:
            product = StoreProduct.objects.get(name=f"test_product{i}")
            product.delete()
        except Exception as e:
            logger.error(f"Failed to get user user{i}: {e}")
            
        rsp, product = StoreHelper.get_or_create_product(
            ean=f"{i}_f{generate_random_numeric_string(8)}", 
            name=f"test_product{i}", 
            resell_price=generate_random_number(1, 15), 
            discount=generate_random_number(1, 10)/100,
            logger=logger)

    
