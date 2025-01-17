import logging
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

from django.db.models import Sum
from django.db import transaction
from store.webmodels.Customer import Customer
from ..webmodels.StoreProduct import StoreProduct
from ..webmodels.CustomerPurchase import CustomerPurchase
from ..webmodels.CustomerDeposit import CustomerDeposit
#from ..webmodels.CustomerBalance import CustomerBalance
from ..webmodels.ProductRestock import ProductRestock
from django.contrib.auth.models import User, Group

from store.webmodels.StoreCash import StoreCash
from store.webmodels.StoreCashMovement import StoreCashMovement

#from store.helpers.ManageCustomerHelper import ManageCustomerHelper
from rest_framework.response import Response
from rest_framework import status
import traceback

from transactify_service.HttpResponses import HTTPResponses
from .Exceptions import HelperException
import store.StoreLogsDBHandler	  # Import your custom logging here
import logging
class StoreHelper:

    @staticmethod
    def get_stock_quantity(product: StoreProduct, logger: logging.Logger) -> int:
        """
        Calculate the remaining stock for a product.
        """
        try:
            quantity_stock = ProductRestock.get_all_restocks_aggregated(product=product) or 0
            quantity_sold = CustomerPurchase.total_purchases(product=product) or 0
            quantity_left = quantity_stock - quantity_sold
            logger.info(f"{product.name} stock calculation: Stock: {quantity_stock}, Sold: {quantity_sold}. Left: {quantity_left}")
            return quantity_left
        except Exception as e:
            logger.error(f"Error calculating stock quantity for product {product}: {e}."
                          f"\nTraceback: {traceback.format_exc()}")
            raise e

    @staticmethod
    @transaction.atomic
    def customer_purchase(ean: str, quantity: int, card_number: str, logger: logging.Logger) -> tuple[Response, CustomerPurchase]:
        """
        Handle customer purchase transaction with atomic database operations.
        """
        logger.info(f"Initiating purchase of product with EAN {ean}, Quantity: {quantity}, Card Number: {card_number}")
        try:
            try:
                customer = Customer.objects.get(card_number=card_number)
                logger.info(f"Customer information: Name: {customer.user.first_name} {customer.user.last_name}, Balance: {customer.balance}")
            except Customer.DoesNotExist:
                logger.error(f"Customer with card number {card_number} not found.")
                raise HelperException(f"", HTTPResponses.HTTP_STATUS_CUSTOMER_NOT_FOUND(card_number))

            #balance = customer.get_balance(CustomerBalance)  # Change No. #1: Ensure get_balance handles potential None or failure gracefully.
            #if balance is None:
            #    logger.error(f"Balance retrieval failed for customer {card_number}.")
            #    raise HelperException(f"", HTTPResponses.HTTP_STATUS_UPDATE_BALANCE_FAILED(customer, "Balance retrieval failed"))

            try:
                product = StoreProduct.objects.get(ean=ean)
                logger.info(f"Product information: Name: {product.name}, Price: {product.resell_price}€, Total Price: {product.get_final_price}€, Stock: {product.stock_quantity}")

            except StoreProduct.DoesNotExist:
                logger.error(f"Product with EAN {ean} not found.")
                raise HelperException(f"", HTTPResponses.HTTP_STATUS_PRODUCT_NOT_FOUND(ean))

            required_balance = quantity * product.get_final_price
            if customer.balance < required_balance:
                logger.warning(f"Insufficient balance for customer {card_number}.")
                raise HelperException(f"", HTTPResponses.HTTP_STATUS_INSUFFICIENT_BALANCE(card_number, required_balance, customer.balance))

            try:
                left_in_stock = StoreHelper.get_stock_quantity(product, logger)
            except Exception as e:
                logger.error(f"Error calculating stock quantity for product {product}: {e}."
                             f"\nTraceback: {traceback.format_exc()}")
                raise HelperException(f"", HTTPResponses.HTTP_STATUS_PRODUCT_STOCK_UPDATE_FAILED(e))

            if left_in_stock < quantity:
                logger.warning(f"Insufficient stock for product {product.name}.")
                raise HelperException(f"", HTTPResponses.HTTP_STATUS_INSUFFICIENT_STOCK(product.name, left_in_stock, quantity))

            try:
                for i in range(quantity):
                    response, customer_purchase = StoreHelper._customer_add_purchase(
                        customer=customer, amount=product.get_final_price, quantity=1, product=product, logger=logger
                    )
                    if response.status_code != 200:  # Change No. #2: Ensure response tuple is properly unpacked.
                        return response
            except Exception as e:
                logger.error(f"Error during purchase. Cannot add a new purchase: {e}."
                             f"\nTraceback: {traceback.format_exc()}")
                raise HelperException(f"", HTTPResponses.HTTP_STATUS_PURCHASE_FAILED(e))

            try:
                old_stock_quantity = product.stock_quantity
                product.stock_quantity = StoreHelper.get_stock_quantity(product, logger)
                product.total_orders = CustomerPurchase.total_purchases(product, logger)
                product.total_revenue = CustomerPurchase.total_revenue(product, logger)
                product.save()
                if product.stock_quantity <= 0:
                    logger.warning(f"Product {product.name} is now out of stock.")
            except Exception as e:
                logger.error(f"Error updating stock quantity: {e}."
                             f"\nTraceback: {traceback.format_exc()}")
                raise HelperException(f"", HTTPResponses.HTTP_STATUS_PRODUCT_STOCK_UPDATE_FAILED(e))

            logger.info(f"Purchase successful. Updated stock for {product.name}: {product.stock_quantity} (was {old_stock_quantity})")
            return HTTPResponses.HTTP_STATUS_PURCHASE_SUCCESS(product.name), customer_purchase  # Change No. #3: Return actual customer object.

        except Exception as e:
            logger.error(f"Purchase failed due to error: {e}."
                         f"\nTraceback: {traceback.format_exc()}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_PURCHASE_FAILED(e))

    @staticmethod
    @transaction.atomic
    def customer_add_deposit(customer: Customer, amount: Decimal, logger: logging.Logger) -> tuple[Response, CustomerDeposit]:
        """
        Add a deposit to a customer's account and log the transaction.
        """
        logger.info(f"Adding deposit for customer {customer} with amount {amount}.")
        if amount <= 0:
            msg = f"Invalid deposit amount for customer {customer}. Must be greater than 0 (was {amount})."
            logger.error(msg)
            raise HelperException(msg, HTTPResponses.HTTP_STATUS_UPDATE_BALANCE_FAILED(customer, msg))
        
        try:
            amount = Decimal(amount)
            # round to 2 decimal places
            amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        except Exception as e:
            msg = f"Failed to convert amount to Decimal for customer {customer}: {e}."
            logger.error(f"{msg}\n\nTraceback:\n {traceback.format_exc()}\n\n")
            raise HelperException(msg, HTTPResponses.HTTP_STATUS_NOT_DECIMAL("amount", type(amount), msg))

        try:
            customer.total_deposits += 1
            customer.balance += amount
            customer.save()
            logger.info(f"Updated balance for customer {customer}: {customer.balance}.")
        except Exception as e:
            logger.error(f"Failed to update customer balance for {customer}: {e}."
                         f"\nTraceback: {traceback.format_exc()}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_UPDATE_BALANCE_FAILED(customer, e))

        try:
            deposit_entry = CustomerDeposit.objects.create(
                customer=customer,
                customer_balance=customer.balance,
                amount=amount
            )
            logger.info(f"Logged deposit for customer {customer}: {deposit_entry}.")
        except Exception as e:
            logger.error(f"Failed to log deposit for customer {customer}: {e}."
                         f"\nTraceback: {traceback.format_exc()}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_UPDATE_DEPOSIT_FAILED(customer, e))

        try:
            total_deposits = customer.get_total_deposit_amount()
            total_purchases = customer.get_total_purchase_amount()

            if Decimal(total_deposits) - Decimal(total_purchases) != Decimal(customer.balance):  # Change No. #4: Replace float comparisons with Decimal.
                logger.error(f"Balance mismatch for customer {customer}. Total Deposits: {total_deposits}, Total Purchases: {total_purchases}, Balance: {customer.balance}")
                raise HelperException(f"", HTTPResponses.HTTP_STATUS_BALANCE_MISMATCH(customer))
        except Exception as e:
            logger.error(f"Failed to validate balance for customer {customer}: {e}."
                         f"\nTraceback: {traceback.format_exc()}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_UPDATE_DEPOSIT_FAILED(customer, e))

        return HTTPResponses.HTTP_STATUS_UPDATE_DEPOSIT_SUCCESS(customer), deposit_entry

    @staticmethod
    @transaction.atomic
    def restock_product(ean: str, quantity: int, purchase_price: Decimal, logger: logging.Logger,
                        auth_user: User, used_store_equity: bool = True, 
                        ) -> tuple[Response, ProductRestock]:
        """
        Restock a product and update its stock quantity.
        """
        logger.info(f"Restocking product with EAN {ean}, Quantity: {quantity}, Purchase Price: {purchase_price}")



        try:
            product = StoreProduct.objects.get(ean=ean)
        except StoreProduct.DoesNotExist:
            logger.error(f"Product with EAN {ean} does not exist.")
            raise HelperException(str(e), HTTPResponses.HTTP_STATUS_PRODUCT_NOT_FOUND(ean))

        try:
            total_cost=purchase_price * quantity
            if used_store_equity:
                # Create a new StoreCashWithdraw record
                try:
                    cash_movement = StoreCashMovement.objects.create(amount=total_cost,
                                                                    user=auth_user)
                    cash_movement.withdraw()
                except Exception as e:
                    logger.error(f"Error during restocking. Cannot create StoreCashWithdraw. Error: {e}.\nTraceback: {traceback.format_exc()}")
                    raise HelperException(str(e), HTTPResponses.HTTP_STATUS_RESTOCK_FAILED(e))
            else:
                # Create a new StoreCashDeposit record
                try:
                    cash_movement = StoreCashMovement.objects.create(amount=total_cost,
                                                                user=auth_user)
                    cash_movement.deposit()
                except Exception as e:
                    logger.error(f"Error during restocking. Cannot create StoreCashDeposit. Error: {e}.\nTraceback: {traceback.format_exc()}")
                    raise HelperException(str(e), HTTPResponses.HTTP_STATUS_RESTOCK_FAILED(e))
            
            product_restock = ProductRestock.objects.create(
                product=product, # Product is wrong
                quantity=quantity,
                purchase_price=purchase_price,
                total_cost=total_cost,
                cash_movement_type=cash_movement
            )
        except Exception as e:
            logger.error(f"Error during restocking. Cannot create ProductRestock. Error: {e}.\nTraceback: {traceback.format_exc()}")
            raise HelperException(str(e), HTTPResponses.HTTP_STATUS_RESTOCK_FAILED(e))

        
            
            
        try:
            product.stock_quantity = StoreHelper.get_stock_quantity(product, logger)
            product.save()
            logger.info(f"Restock successful. Updated stock for {product.name}: {product.stock_quantity}")
            return HTTPResponses.HTTP_STATUS_RESTOCK_SUCCESS(product.name), product_restock

        except Exception as e:
            logger.error(f"Error during restocking: {e}.\nTraceback: {traceback.format_exc()}")
            raise HelperException(str(e), HTTPResponses.HTTP_STATUS_RESTOCK_FAILED(e))

    @staticmethod
    @transaction.atomic
    def create_new_customer(username: str, first_name: str, last_name: str, email: str, balance: Decimal, card_number: str, logger: logging.Logger) -> tuple[Response, Customer]:
        """
        Create and save a new customer along with their initial deposit.
        """
        logger.info(f"Creating new customer: Username {username}, Email {email}, Balance {balance}.")

        # convert the card number to a string
        card_number = str(card_number)
        if card_number is None or len(card_number) == 0 or card_number.strip == "":
            logger.error(f"Invalid card number for customer {username}.")
            raise HelperException(f"Invalid card number for customer {username}.", 
                                  HTTPResponses.HTTP_STATUS_CUSTOMER_CREATE_FAILED(username, "Invalid card number"))
        
        try:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            logger.info(f"User created for customer {username}.")
        except Exception as e:
            msg = f"Failed to create user for customer {username}: {e}."
            logger.error(f"{msg}\n\nTraceback:\n {traceback.format_exc()}\n\n")
            raise HelperException(msg, HTTPResponses.HTTP_STATUS_CUSTOMER_CREATE_FAILED(username, e))

        try:
            group, _ = Group.objects.get_or_create(name="Customer")
        except Exception as e:
            logger.error(f"Failed to create customer group: {e}."
                         f"\nTraceback: {traceback.format_exc()}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_GROUP_CREATE_FAILED("Customer", e))  # Change No. #5: Ensure group name is correctly passed.

        try:
            customer = Customer.objects.create(
                user=user,
                card_number=card_number,
                issued_at=datetime.now()
            )
            customer.user.groups.add(group)
        except Exception as e:
            logger.error(f"Failed to create customer record for {username}: {e}."
                         f"\nTraceback: {traceback.format_exc()}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_CUSTOMER_CREATE_FAILED(username, e))

        if balance > 0:
            try:
                response, deposit_entry = StoreHelper.customer_add_deposit(customer, balance, logger)  # Change No. #6: Ensure correct unpacking of return values.
                #customer_balance = CustomerBalance.objects.get(customer=customer)
                if response.status_code != 200:
                    return response
                logger.info(f"Initial deposit logged for customer {username}: {customer.balance}.")
            except Exception as e:
                logger.error(f"Failed to log initial deposit for customer {username}: {e}")
                raise HelperException(
                    f"Failed to log initial deposit for customer {username}: {e}", 
                    HTTPResponses.HTTP_STATUS_CUSTOMER_CREATE_FAILED(username, e))
            customer.save()
            logger.info(f"Customer record created for {username}.")
        return HTTPResponses.HTTP_STATUS_CUSTOMER_CREATE_SUCCESS(username), customer
  
  	# =========================================================================================================
    # Private methods
    # =========================================================================================================

    @staticmethod
    @transaction.atomic
    def get_or_create_product(ean: str, name: str, resell_price: Decimal, discount: Decimal, logger: logging.Logger) -> tuple[Response, StoreProduct]:
        """
        Get or create a product by EAN, and update its details if it exists.
        """
        # check if all required fields are present
        if not ean or not name or not resell_price:
            logger.error("Missing required fields for product creation.")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_PRODUCT_CREATE_FAILED(ean, "Missing required fields"))
            
        if discount < 0 or discount > 100:
            logger.error(f"Invalid discount value for product '{name}': {discount}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_PRODUCT_CREATE_FAILED(ean, f"Invalid discount value: {discount}"))
        
        if resell_price < 0:
            logger.error(f"Invalid resell price for product '{name}': {resell_price}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_PRODUCT_CREATE_FAILED(ean, f"Invalid resell price: {resell_price}"))
        
        logger.info(f"Creating or retrieving product '{name}' with EAN '{ean}' (Resell Price: {resell_price})")
        try:
            product, created = StoreProduct.objects.get_or_create(ean=ean)
            product.name = name
            product.resell_price = resell_price
            product.discount = discount
            product.save()
        except Exception as e:
            logger.error(f"Error during product creation: {e}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_PRODUCT_CREATE_FAILED(ean, e))

        if created:
            logger.info(f"New product created: {product}")
            return HTTPResponses.HTTP_STATUS_PRODUCT_CREATE_SUCCESS(ean), product  # Change No. #7: Ensure the response contains relevant EAN.
        else:
            logger.info(f"Existing product updated: {product}")
            return HTTPResponses.HTTP_STATUS_PRODUCT_UPDATE_SUCCESS(ean), product  # Change No. #7: Ensure the response contains relevant EAN.

    @staticmethod
    @transaction.atomic
    def _customer_add_purchase(customer: Customer, amount: Decimal, quantity: int, product: StoreProduct, logger: logging.Logger) -> tuple[Response, CustomerPurchase]:
        """
        Process a purchase for a customer and update their balance and transaction logs.
        """
        
        try:
            amount *= quantity
            amount = Decimal(amount)
            logger.info(f"Processing purchase for customer {customer}: Product {product}, Quantity {quantity}, Amount {amount}.")
        except Exception as e:
            logger.error(f"Failed to convert amount to Decimal for customer {customer}: {e}.\nTraceback: {traceback.format_exc()}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_NOT_DECIMAL("amount", type(amount), e))

        try:
            #customer_balance, _ = CustomerBalance.objects.get_or_create(customer=customer)
            customer.total_purchases += 1
            customer.balance -= amount
            customer.save()
            logger.info(f"Updated balance for customer {customer}: {customer.balance}.")
        except Exception as e:
            logger.error(f"Failed to update customer balance during purchase for {customer}: {e}.\nTraceback: {traceback.format_exc()}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_UPDATE_BALANCE_FAILED(customer, e))

        try:
            # id = models.AutoField(primary_key=True)
            # product = models.ForeignKey(StoreProduct, on_delete=models.CASCADE)
            # # The quantity of the product purchased
            # quantity = models.PositiveIntegerField()
            # # The total price the product was purchased for
            # purchase_price = models.DecimalField(max_digits=10, decimal_places=2)

            # # The total revenue generated by the purchase
            # revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
            # # The total expenses incurred by the purchase
            # expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
            # # The total revenue generated by the purchase
            # profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)

            # # The customer who made the purchase
            # customer = models.ForeignKey(Customer, on_delete=models.CASCADE,  db_constraint=False )
            # # The customer's balance after the deposit
            # customer_balance = models.DecimalField(max_digits=10, decimal_places=2)
            # # The date the deposit was made
            # purchase_date = models.DateTimeField(auto_now_add=True)

            purchase_entry = CustomerPurchase.objects.create(
                product=product,
                quantity=quantity,
                purchase_price=amount,
                customer=customer,
                customer_balance=customer.balance
            )
            purchase_entry.calculate_profit(logger)
            logger.info(f"Logged purchase for customer {customer}: {purchase_entry}.")
        except Exception as e:
            purchase_entry.payment_status = "error"
            purchase_entry.order_status = "error"
            logger.error(f"Failed to log purchase for customer {customer}: {e}.\nTraceback: {traceback.format_exc()}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_PURCHASE_FAILED(customer, e))

        try:
            total_deposit = customer.get_total_deposit_amount()
            total_purchases = customer.get_total_purchase_amount()

            if Decimal(total_deposit) - Decimal(total_purchases) != Decimal(customer.balance):  # Change No. #8: Replace float comparisons with Decimal.
                logger.error(f"Balance mismatch after purchase for customer {customer}. Total Deposits: {total_deposit}, Total Purchases: {total_purchases}, Balance: {customer.balance}")
                purchase_entry.payment_status = "failed"
                purchase_entry.order_status = "cancelled"
                raise HelperException(f"", HTTPResponses.HTTP_STATUS_BALANCE_MISMATCH(customer))
        except Exception as e:
            logger.error(f"Failed to validate balance after purchase for customer {customer}: {e}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_PURCHASE_FAILED(e))
        
        purchase_entry.order_status = "completed"
        purchase_entry.payment_status = "paid"
        purchase_entry.save()

        return HTTPResponses.HTTP_STATUS_PURCHASE_SUCCESS(customer), purchase_entry
