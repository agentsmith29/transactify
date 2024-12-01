from ..webmodels.StoreProduct import StoreProduct
from ..webmodels.CustomerPurchase import CustomerPurchase
from ..webmodels.CustomerDeposit import CustomerDeposit
from ..webmodels.CustomerBalance import CustomerBalance

from ..webmodels.ProductRestock import ProductRestock

from cashlessui.models import Customer
from decimal import Decimal
from django.db.models import Sum

from django.contrib.auth.models import User, Group

import logging

from datetime import datetime

class ManageCustomerHelper():

    def customer_add_deposit(customer: Customer, amount: Decimal):
        logger = logging.getLogger('store')
        try:
            amount = Decimal(amount)
        except Exception as e:
            logger.error(f"[Deposit] Failed to convert amount to float for customer {customer}: {e}")
            raise e
        # Get or create the CustomerBalance object
        try:
            customer_balance, inst = CustomerBalance.objects.get_or_create(
                customer=customer
            )
            # Increment the total number of deposits
            customer_balance.total_deposits += 1
            # Update the balance
            customer_balance.balance = customer_balance.balance + amount
            customer_balance.save()
        except Exception as e:
            logger.error(f"[Deposit] Failed to add deposit for customer {customer}: {e}")
            raise e

        try:
            # Log the deposit
            deposit_entry = CustomerDeposit.objects.create(
                customer=customer,
                customer_balance=customer_balance.balance,
                amount=amount,
            )
        except Exception as e:
            logger.error(f"[Deposit] Failed to log deposit for customer {customer}: {e}")
            raise e
        

        try:
            # Sanity check. All purchases and all deposits must be the same as new_balance
            total_deposit = customer.get_all_deposits_aggregated(CustomerDeposit)
            total_purchases = customer.get_all_purchases_aggregated(CustomerPurchase)
            if float(total_deposit - total_purchases) != float(customer_balance.balance):
                logger.error(f"[Deposit] Deposit failed due to balance mismatch for customer {customer}")
                #return -4, None, None, None
        except Exception as e:
            logger.error(f"[Deposit] Failed to check balance for customer {customer}: {e}")
            raise e

        return customer, customer_balance, deposit_entry
    
    def customer_add_purchase(customer: Customer, amount: Decimal, quantity: Decimal, product: StoreProduct):
        logger = logging.getLogger('Customers Purchase')
         # Make the sale, create a new CustomerPurchase record, to track the sale
       # Get or create the CustomerBalance object
        customer_balance, inst = CustomerBalance.objects.get_or_create(
            customer=customer
        )
        # Increment the total number of deposits
        customer_balance.total_purchases += 1
        # Update the balance
        customer_balance.balance = customer_balance.balance - amount
        customer_balance.save()
        # Log the deposit
        purchase_entry = CustomerPurchase.objects.create(
            product=product, 
            quantity=quantity, purchase_price=amount,
            customer=customer, customer_balance=customer_balance.balance,
            )
        logger.info(f"[PURCHASE] New balance for customer {customer}: {customer_balance.balance}")
        # Sanity check. All purchases and all deposits must be the same as new_balance
        total_deposit = customer.get_all_deposits_aggregated(CustomerDeposit)
        total_purchases = customer.get_all_purchases_aggregated(CustomerPurchase)
        if float(total_deposit - total_purchases) != float(customer_balance.balance):
            logger.error(f"[PURCHASE] Purchase failed due to balance mismatch for customer {customer}")

        return customer, customer_balance, purchase_entry        


    def create_new_customer(username, first_name, last_name, email, balance, card_number):
        """Creates and saves a new customer."""
        # Create the associated User object
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        group = Group.objects.get(name="Customer")

        # Create the Customer object linked to the User
        customer = Customer.objects.create(
            user=user,
            card_number=card_number,
            issued_at=datetime.now(),
        )
        customer.user.groups.add(group)
        customer.save()

        # Log the initial deposit
        try:
            customer, customer_balance, deposit_entry = ManageCustomerHelper.customer_add_deposit(customer, balance)
        except Exception as e:
            logging.getLogger('store').error(f"[Customer] Failed to create new customer: {e}")
        return customer, customer_balance, deposit_entry
