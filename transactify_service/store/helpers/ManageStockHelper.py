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
from ..webmodels.CustomerConfig import CustomerConfig
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
import functools

from transactify_service.settings import CONFIG

from store.helpers.OFFExtractor import OFFExtractor

from django.utils import timezone
from store.helpers.EmailHelper import EmailHelper
from store.mail_html_templates.MailTemplate import MailTemplate
from django.db import models
class StoreHelper:

    def journal_command():
        """ decorator to jurnal the command to a file """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Capture the arguments and store them in self.stored_context
                # Call the original function
                if '__ignore_journal__' in kwargs:
                    kwargs.pop('__ignore_journal__')
                    return func(*args, **kwargs)
                
                result = func(*args, **kwargs)

                # Optionally store the result in context
                with open(CONFIG.webservice.JOURNAL_FILE, "a") as f:
                    f.write(f"# Command: {func.__name__}, Args: {args}, Kwargs: {kwargs}, Result: {result}\n")
                    f.write(f"# Issued at: {datetime.now()}\n")
                    f.write(f"# Result: {result}\n")
                    # Construct the commonad which can be direcly called by python
                    f.write(f"StoreHelper.{func.__name__}(*{args}, **{kwargs})\n\n")
                    
                return result

            return wrapper
        return decorator
    

    @staticmethod
    def get_stock_quantity(product: StoreProduct, logger: logging.Logger, *args, **kwargs) -> int:
        """
        Calculate the remaining stock for a product.
        """
        try:
            quantity_stock = ProductRestock.get_all_restocks_aggregated(product=product, logger=logger) or 0
            quantity_sold = CustomerPurchase.total_purchases(product=product, logger=logger) or 0
            quantity_left = quantity_stock - quantity_sold
            logger.debug(f"{product.name} stock calculation: Stock: {quantity_stock}, Sold: {quantity_sold}. Left: {quantity_left}")
            return quantity_left
        except Exception as e:
            logger.error(f"Error calculating stock quantity for product {product}: {e}."
                          f"\nTraceback: {traceback.format_exc()}")
            raise e

    @staticmethod
    @transaction.atomic
    @journal_command()
    def customer_purchase(ean: str, quantity: int, card_number: str, logger: logging.Logger, prepaid = False, *args, **kwargs) -> tuple[Response, CustomerPurchase]:
        """
        Handle customer purchase transaction with atomic database operations.
        """
        time_start = datetime.now()
        logger.info(f"Initiating purchase of product with EAN {ean}, Quantity: {quantity}, Card Number: {card_number}")
        try:
            try:
                customer = Customer.objects.get(card_number=card_number)
                logger.info(f"Customer information: Name: {customer.user.first_name} {customer.user.last_name}, Balance: {customer.balance}")
            except Customer.DoesNotExist:
                logger.error(f"Customer with card number {card_number} not found.")
                raise HelperException(f"Customer with card number {card_number} not found.", HTTPResponses.HTTP_STATUS_CUSTOMER_NOT_FOUND(card_number))

            #balance = customer.get_balance(CustomerBalance)  # Change No. #1: Ensure get_balance handles potential None or failure gracefully.
            #if balance is None:
            #    logger.error(f"Balance retrieval failed for customer {card_number}.")
            #    raise HelperException(f"", HTTPResponses.HTTP_STATUS_UPDATE_BALANCE_FAILED(customer, "Balance retrieval failed"))

            try:
                product = StoreProduct.objects.get(ean=ean)
                logger.info(f"Product information: Name: {product.name}, Price: {product.resell_price}€, Total Price: {product.final_price}€, Stock: {product.stock_quantity}")

            except StoreProduct.DoesNotExist:
                logger.error(f"Product with EAN {ean} not found.")
                raise HelperException(f"", HTTPResponses.HTTP_STATUS_PRODUCT_NOT_FOUND(ean))

            required_balance = quantity * product.final_price
            
            if customer.config.auto_deposit or prepaid:
                StoreHelper.customer_add_deposit(customer, required_balance, logger)

            
            if customer.balance < required_balance:
                logger.warning(f"Insufficient balance for customer {card_number}.")
                raise HelperException(f"Insufficient balance for customer {card_number}.",
                                       HTTPResponses.HTTP_STATUS_INSUFFICIENT_BALANCE(card_number, required_balance, customer.balance))

            try:
                left_in_stock = StoreHelper.get_stock_quantity(product, logger)
            except Exception as e:
                logger.error(f"Error calculating stock quantity for product {product}: {e}."
                             f"\nTraceback: {traceback.format_exc()}")
                raise HelperException(f"", HTTPResponses.HTTP_STATUS_PRODUCT_STOCK_UPDATE_FAILED(e))

            if left_in_stock < quantity:
                logger.warning(f"Insufficient stock for product {product.name}.")
                raise HelperException(f"Insufficient stock for product {product.name}.", 
                                      HTTPResponses.HTTP_STATUS_INSUFFICIENT_STOCK(product.name, left_in_stock, quantity))



            try:
                #for i in range(quantity):
                response, customer_purchase = StoreHelper._customer_add_purchase(
                    customer=customer, amount=product.final_price, quantity=quantity, product=product, logger=logger
                )
                if response.status_code != 200:  # Change No. #2: Ensure response tuple is properly unpacked.
                    return response
            except Exception as e:
                logger.error(f"Error during purchase. Cannot add a new purchase: {e}."
                             f"\nTraceback: {traceback.format_exc()}")
                raise HelperException(f"Error during purchase. Cannot add a new purchase: {e}.", HTTPResponses.HTTP_STATUS_PURCHASE_FAILED(e))

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

            try:
                MailTemplate.send_mail_template_purchase(
                    customer,
                    customer_purchase.id, 
                    product.name, required_balance, 
                    datetime.now().strftime("%d/%m/%Y"),
                    CONFIG.webservice.FRIENDLY_NAME,
                    logger, send_to_admin=True)
            except Exception as e:
                logger.warning(f"Error sending email to customer {card_number}: {e}.")
                                  
            logger.info(f"Purchase successful. Updated stock for {product.name}: {product.stock_quantity} (was {old_stock_quantity})")
            time_end = datetime.now()
            logger.debug(f"Purchase completed in {time_end - time_start}s.")
            return HTTPResponses.HTTP_STATUS_PURCHASE_SUCCESS(product.name), customer_purchase  # Change No. #3: Return actual customer object.

        except Exception as e:
            logger.error(f"Purchase failed due to error: {e}."
                         f"\nTraceback: {traceback.format_exc()}")
                         
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_PURCHASE_FAILED(e))

    def customer_multiple_purchase(products: list, customer, logger: logging.Logger, prepaid = False, *args, **kwargs):
        pass

    
    @staticmethod
    @transaction.atomic
    @journal_command()
    def customer_add_deposit(customer: Customer, amount: Decimal, logger: logging.Logger, *args, **kwargs) -> tuple[Response, CustomerDeposit]:
        """
        Add a deposit to a customer's account and log the transaction.
        """
        try:
            amount = Decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except Exception as e:
            msg = f"Invalid deposit amount: {amount}. Must be a valid decimal."
            logger.error(f"{msg}\n\nTraceback:\n {traceback.format_exc()}\n\n")
            raise HelperException(msg, HTTPResponses.HTTP_STATUS_NOT_DECIMAL("amount", type(amount), msg))

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
            expected_balance = total_deposits - total_purchases
            if not Decimal(customer.balance).quantize(Decimal("0.01")) == expected_balance.quantize(Decimal("0.01")):
                logger.error(f"Balance mismatch for customer {customer}. Total Deposits: {total_deposits}, Total Purchases: {total_purchases}, Balance: {customer.balance}")
                raise HelperException(f"Balance mismatch for customer {customer}.", HTTPResponses.HTTP_STATUS_BALANCE_MISMATCH(customer))
        except Exception as e:
            logger.error(f"Failed to validate balance for customer {customer}: {e}."
                         f"\nTraceback: {traceback.format_exc()}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_UPDATE_DEPOSIT_FAILED(e))

        try:
            MailTemplate.send_mail_template_new_deposit(
                customer, amount, 
                customer.balance, 
                datetime.now().strftime("%d.%m.%Y"), 
                CONFIG.webservice.FRIENDLY_NAME, 
                logger, send_to_admin=True)
        except Exception as e:
            logger.warning(f"Error sending email to customer {customer}: {e}.")

        return HTTPResponses.HTTP_STATUS_UPDATE_DEPOSIT_SUCCESS(customer), deposit_entry

    @staticmethod
    @transaction.atomic
    @journal_command()
    def customer_remove_deposit(customer: Customer, amount: Decimal, logger: logging.Logger, *args, **kwargs) -> tuple[Response, CustomerDeposit]:
        """
        Add a deposit to a customer's account and log the transaction.
        """
        try:
            amount = Decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except Exception as e:
            msg = f"Invalid amount: {amount}. Must be a valid decimal."
            logger.error(f"{msg}\n\nTraceback:\n {traceback.format_exc()}\n\n")
            raise HelperException(msg, HTTPResponses.HTTP_STATUS_NOT_DECIMAL("amount", type(amount), msg))

        logger.info(f"Removing deposit for customer {customer} with amount {amount}.")
        if amount >= 0:
            msg = f"Invalid amount for customer {customer}. Must be smaller than 0 (was {amount})."
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
            customer.balance -= amount
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
            logger.info(f"Logged removed amount for customer {customer}: {deposit_entry}.")
        except Exception as e:
            logger.error(f"Failed to removed amount for customer {customer}: {e}."
                         f"\nTraceback: {traceback.format_exc()}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_UPDATE_DEPOSIT_FAILED(customer, e))

        try:
            total_deposits = customer.get_total_deposit_amount()
            total_purchases = customer.get_total_purchase_amount()
            expected_balance = total_deposits - total_purchases
            if not Decimal(customer.balance).quantize(Decimal("0.01")) == expected_balance.quantize(Decimal("0.01")):
                logger.error(f"Balance mismatch for customer {customer}. Total Deposits: {total_deposits}, Total Purchases: {total_purchases}, Balance: {customer.balance}")
                raise HelperException(f"Balance mismatch for customer {customer}.", HTTPResponses.HTTP_STATUS_BALANCE_MISMATCH(customer))
        except Exception as e:
            logger.error(f"Failed to validate balance for customer {customer}: {e}."
                         f"\nTraceback: {traceback.format_exc()}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_UPDATE_DEPOSIT_FAILED(e))

        try:
            MailTemplate.send_mail_template_new_deposit(
                customer, amount, 
                customer.balance, 
                datetime.now().strftime("%d.%m.%Y"), 
                CONFIG.webservice.FRIENDLY_NAME, 
                logger, send_to_admin=True)
        except Exception as e:
            logger.warning(f"Error sending email to customer {customer}: {e}.")

        return HTTPResponses.HTTP_STATUS_UPDATE_DEPOSIT_SUCCESS(customer), deposit_entry

    @staticmethod
    @transaction.atomic
    @journal_command()
    def customer_remove_deposit(customer: Customer, deposit_id: int, logger: logging.Logger, *args, **kwargs) -> tuple[Response, CustomerDeposit]:
        deposit_id = int(deposit_id)
        try:
            deposit = CustomerDeposit.objects.get(id=deposit_id)
        except CustomerDeposit.DoesNotExist:
            logger.error(f"Deposit with ID {deposit_id} not found.")
            raise HelperException(f"Deposit with ID {deposit_id} not found.", HTTPResponses.HTTP_STATUS_DEPOSIT_NOT_FOUND(deposit_id))
        
        StoreHelper.customer_add_deposit(customer, -amount, logger)

    @staticmethod
    @transaction.atomic
    @journal_command()
    def restock_product(ean: str, quantity: int, purchase_price: Decimal, auth_user: User, 
                        logger: logging.Logger, used_store_equity: bool = True, 
                        ) -> tuple[Response, ProductRestock]:
        """
        Restock a product and update its stock quantity.
        """
        purchase_price = Decimal(purchase_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if quantity <= 0:
            logger.error(f"Invalid restock quantity for product with EAN {ean}: {quantity}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_RESTOCK_FAILED(f"Invalid restock quantity for product {ean}")) 
        
        logger.info(f"Restocking product with EAN {ean}: Quantity: {quantity} | Purchase Price: {purchase_price}")

        try:
            product = StoreProduct.objects.get(ean=ean)
            calculated_stock_quantity = StoreHelper.get_stock_quantity(product, logger)

            old_stock_quantity = product.stock_quantity
            logger.debug(f"Product information: Name: {product.name}, Stock: {old_stock_quantity} (calculated: {calculated_stock_quantity})")
           
        except StoreProduct.DoesNotExist:
            logger.error(f"Product with EAN {ean} does not exist.")
            raise HelperException(f"Product with EAN {ean} does not exist.", HTTPResponses.HTTP_STATUS_PRODUCT_NOT_FOUND(ean))

        if int(old_stock_quantity) != int(calculated_stock_quantity):
            logger.error(f"Stock quantity mismatch for product {product.name}. Expected: {calculated_stock_quantity}, Actual: {old_stock_quantity}")
            raise HelperException(f"The stock quantity tracked and calculated does not match.", HTTPResponses.HTTP_STATUS_PRODUCT_STOCK_UPDATE_FAILED(product.name))
        

        try:
            total_cost = purchase_price * quantity
            logger.debug(f"Total cost for restocking: {total_cost}")
            if used_store_equity:
                # Create a new StoreCashWithdraw record
                try:
                    cash_movement = StoreCashMovement.objects.create(amount=total_cost, user=auth_user)
                    cash_movement.withdraw()
                    logger.info(f"Store equity used for restocking: {total_cost}")
                except Exception as e:
                    logger.error(f"Error during restocking. Cannot create StoreCashWithdraw. Error: {e}.\nTraceback: {traceback.format_exc()}")
                    raise HelperException(str(e), HTTPResponses.HTTP_STATUS_RESTOCK_FAILED(e))
            else:
                # Create a new StoreCashDeposit record
                try:
                    cash_movement = StoreCashMovement.objects.create(amount=total_cost,
                                                                user=auth_user)
                    cash_movement.deposit()
                    logger.info(f"New cash deposit for restocking: {total_cost}")
                except Exception as e:
                    logger.error(f"Error during restocking. Cannot create StoreCashDeposit. Error: {e}.\nTraceback: {traceback.format_exc()}")
                    raise HelperException(str(e), HTTPResponses.HTTP_STATUS_RESTOCK_FAILED(e))
        except Exception as e:
            logger.error(f"Error during restocking. Cannot create cash movement. Error: {e}.\nTraceback: {traceback.format_exc()}")
            raise HelperException(str(e), HTTPResponses.HTTP_STATUS_RESTOCK_FAILED)
                                  
        try:    
            product_restock = ProductRestock.objects.create(
                product=product, # Product is wrong
                quantity=quantity,
                purchase_price=purchase_price,
                total_cost=total_cost,
                cash_movement_type=cash_movement
            )
            # get the previous ProductRestock and set undo_allowed to False
            previous_restock = ProductRestock.get_all_restocks(product).exclude(id=product_restock.id).last()
            if previous_restock:
                previous_restock.undo_allowed = False
                previous_restock.save()
                logger.info(f"Previous restock {previous_restock.id} set to not undoable.")

            logger.debug(f"Creating new ProductRestock record for product {product.name}: {product_restock}")
        except Exception as e:
            logger.error(f"Error during restocking. Cannot create ProductRestock. Error: {e}.\nTraceback: {traceback.format_exc()}")
            raise HelperException(str(e), HTTPResponses.HTTP_STATUS_RESTOCK_FAILED(e))

        
        try:
            product.stock_quantity +=  quantity
            new_stock_quantity = product.stock_quantity
            new_calculated_stock_quantity=  StoreHelper.get_stock_quantity(product, logger)
            product.save()
        except Exception as e:
            logger.error(f"Error during restocking: {e}.\nTraceback: {traceback.format_exc()}")
            raise HelperException(str(e), HTTPResponses.HTTP_STATUS_RESTOCK_FAILED(e))

        if int(new_stock_quantity) != int(new_calculated_stock_quantity):
            logger.error(f"The stock quantity tracked and calculated for {product.name} does not match. Expected: {new_calculated_stock_quantity}, Actual: {new_stock_quantity}")
            raise HelperException(f"The stock quantity tracked and calculated does not match.", HTTPResponses.HTTP_STATUS_PRODUCT_STOCK_UPDATE_FAILED(product.name))
        


        if old_stock_quantity == product.stock_quantity:
            logger.error(f"The stock has not been updated for product {product.name}. Expected: {old_stock_quantity + quantity}, Actual: {product.stock_quantity}")
            raise HelperException(f"The stock quantity tracked and calculated for {product.name} does not match.", 
                                  HTTPResponses.HTTP_STATUS_PRODUCT_STOCK_UPDATE_FAILED(f"Stock quantity mismatch for product {product.name}"))
        else:
            logger.info(f"Product restocked: {product.name} | Stock: {product.stock_quantity} (was {old_stock_quantity})")
            return HTTPResponses.HTTP_STATUS_RESTOCK_SUCCESS(product.name), product_restock

    
    @staticmethod
    @transaction.atomic
    @journal_command()
    def delete_restock_entry(restock_id: int, auth_user: User,  logger: logging.Logger, used_store_equity: bool = True,  ) -> tuple[Response, ProductRestock]:
        """
        Remove a restock entry, update stock levels accordingly, and handle any necessary store cash adjustments.
        """
        try:
            restock = ProductRestock.objects.get(id=restock_id)
        except Exception as e:
            logger.error(f"Error retrieving restock entry: {e}\nTraceback: {traceback.format_exc()}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_RESTOCK_FAILED(e)) 
        
        # Check if it is allowed to delete the object
        if not restock.undo_allowed:
            logger.error(f"Cannot remove restock entry {restock.id} for product {restock.product.name}.")
            raise HelperException(f"Cannot remove restock entry {restock.id} for product {restock.product.name}.", 
                                  HTTPResponses.HTTP_STATUS_RESTOCK_FAILED(f"Cannot remove restock entry {restock.id} for product {restock.product.name}"))


        logger.info(f"Removing restock entry: {restock.id} for product {restock.product.name}")

        try:
            product = restock.product
            old_stock_quantity = product.stock_quantity
            calculated_stock_quantity = StoreHelper.get_stock_quantity(product, logger)
        except Exception as e:
            logger.error(f"Error retrieving product or calculating stock quantity: {e}\nTraceback: {traceback.format_exc()}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_PRODUCT_STOCK_UPDATE_FAILED(e))

        if int(old_stock_quantity) != int(calculated_stock_quantity):
            logger.error(f"Stock quantity mismatch for product {product.name}. Expected: {calculated_stock_quantity}, Actual: {old_stock_quantity}")
            raise HelperException(f"Stock quantity mismatch for product {product.name}.", HTTPResponses.HTTP_STATUS_PRODUCT_STOCK_UPDATE_FAILED(product.name))

        try:
            restock_quantity = restock.quantity
            product.stock_quantity -= restock_quantity
            if product.stock_quantity < 0:
                logger.warning(f"Stock quantity for product {product.name} would be negative. Resetting to zero.")
                product.stock_quantity = 0
            product.save()
        except Exception as e:
            logger.error(f"Error updating stock quantity after removing restock: {e}\nTraceback: {traceback.format_exc()}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_PRODUCT_STOCK_UPDATE_FAILED(e))

        if used_store_equity:
            try:
                cash_movement = StoreCashMovement.objects.create(amount=restock.total_cost, user=auth_user)
                cash_movement.deposit()
                logger.info(f"Store equity refunded for removed restock: {restock.total_cost}")
            except Exception as e:
                logger.error(f"Error refunding store equity: {e}\nTraceback: {traceback.format_exc()}")
                raise HelperException(str(e), HTTPResponses.HTTP_STATUS_RESTOCK_FAILED(e))
        
        try:
            restock.delete()
            logger.info(f"Restock entry {restock.id} successfully removed.")
        except Exception as e:
            logger.error(f"Error deleting restock entry: {e}\nTraceback: {traceback.format_exc()}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_RESTOCK_FAILED(e))
        
        return HTTPResponses.HTTP_STATUS_RESTOCK_ENTRY_DELETE_SUCCESS(), restock


    @staticmethod
    @transaction.atomic
    @journal_command()
    def create_new_customer(username: str, first_name: str, last_name: str, email: str, balance: Decimal, card_number: str, logger: logging.Logger, *args, **kwargs) -> tuple[Response, Customer]:
        """
        Create and save a new customer along with their initial deposit.
        """
        logger.info(f"Creating new customer: Username {username}, Email {email}, Balance {balance}.")

        if card_number is None or len(card_number) == 0 or card_number.strip() == "":
                logger.error(f"Invalid card number for customer {username}.")
                raise HelperException(f"Invalid card number for customer {username}.", 
                                    HTTPResponses.HTTP_STATUS_CUSTOMER_CREATE_FAILED(username, "Invalid card number"))
            
            
        # Validate the card number
        card_number = str(card_number).strip()
        if not card_number:
            msg = f"Invalid card number for customer {username}."
            logger.error(msg)
            raise HelperException(msg, HTTPResponses.HTTP_STATUS_CUSTOMER_CREATE_FAILED(username, "Invalid card number"))

        # Check for duplicate card numbers
        if Customer.objects.filter(card_number=card_number).exists():
            msg = f"Card number {card_number} already exists for another customer."
            logger.error(msg)
            raise HelperException(msg, HTTPResponses.HTTP_STATUS_CUSTOMER_CREATE_FAILED(username, msg))

        # Validate balance
        if balance < 0:
            msg = f"Balance cannot be negative for customer {username}. Provided: {balance}."
            logger.error(msg)
            raise HelperException(msg, HTTPResponses.HTTP_STATUS_CUSTOMER_CREATE_FAILED(username, msg))

        try:
            # Create the User
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
            # Assign the user to the "Customer" group
            group, _ = Group.objects.get_or_create(name="Customer")
            user.groups.add(group)
        except Exception as e:
            msg = f"Failed to assign user {username} to Customer group: {e}."
            logger.error(f"{msg}\n\nTraceback:\n {traceback.format_exc()}\n\n")
            raise HelperException(msg, HTTPResponses.HTTP_STATUS_GROUP_CREATE_FAILED("Customer", e))

        try:
            # Create the Customer
            customer = Customer.objects.create(
                user=user,
                card_number=card_number,
                issued_at=timezone.now(),
            )
        except Exception as e:
            msg = f"Failed to create customer record for {username}: {e}."
            logger.error(f"{msg}\n\nTraceback:\n {traceback.format_exc()}\n\n")
            raise HelperException(msg, HTTPResponses.HTTP_STATUS_CUSTOMER_CREATE_FAILED(username, e))

        # Add an initial deposit if balance > 0
        if balance > 0:
            try:
                response, deposit_entry = StoreHelper.customer_add_deposit(customer, balance, logger, __ignore_journal__=True)
                if response.status_code != 200:
                    return response
                logger.info(f"Initial deposit logged for customer {username}: {customer.balance}.")
            except Exception as e:
                msg = f"Failed to log initial deposit for customer {username}: {e}."
                logger.error(f"{msg}\n\nTraceback:\n {traceback.format_exc()}\n\n")
                raise HelperException(msg, HTTPResponses.HTTP_STATUS_CUSTOMER_CREATE_FAILED(username, e))

        customer.save()
        logger.info(f"Customer record created for {username}.")
        return HTTPResponses.HTTP_STATUS_CUSTOMER_CREATE_SUCCESS(username), customer


    @staticmethod
    @transaction.atomic
    def update_customer_details(customer: Customer, 
                                card_number: str = None,
                                first_name: str = None,  
                                last_name: str = None,
                                email: str = None, password: str = None, 
                                autodeposit: bool = None,
                                logger: logging.Logger = None
    ) -> tuple[Response, Customer]:
        """
        Update customer details including first name, last name, email, and password.
        
        Args:
            card_number (str): The unique ID (or card number) of the customer.
            first_name (str, optional): The new first name.
            last_name (str, optional): The new last name.
            email (str, optional): The new email.
            password (str, optional): The new password.
            logger (logging.Logger, optional): Logger instance for detailed logging.

        Returns:
            tuple: (Response, Customer) - HTTP Response status and updated customer instance.
        """
        if logger is None:
            logger = logging.getLogger(__name__)

        logger.info(f"Initiating update for customer ID: {customer.id}.")

        # Fetch the customer record
        try:
            user = customer.user
            logger.info(f"Customer record found: {user.username} (Card Number: {customer.id}).")
        except Customer.DoesNotExist:
            msg = f"Customer with ID {customer.id} not found."
            logger.error(msg)
            return HTTPResponses.HTTP_STATUS_CUSTOMER_UPDATE_FAILED(customer.id, msg), None
        except Exception as e:
            msg = f"Unexpected error retrieving customer {customer.id}: {e}."
            logger.error(f"{msg}\n\nTraceback:\n{traceback.format_exc()}\n")
            return HTTPResponses.HTTP_STATUS_CUSTOMER_UPDATE_FAILED(customer.id, msg), None

        updated_fields = {}

        try:
            if card_number is not None:
                # Check for duplicate card numbers
                if Customer.objects.filter(card_number=card_number).exclude(pk=customer.id).exists():
                    msg = f"Card number {card_number} is already in use by another customer."
                    logger.error(msg)
                    return HTTPResponses.HTTP_STATUS_CUSTOMER_UPDATE_FAILED(customer.id, msg), None

                customer.card_number = card_number.strip()
                updated_fields["card_number"] = card_number.strip

            # Apply changes if parameters are provided
            if first_name is not None:
                user.first_name = first_name.strip()
                updated_fields["first_name"] = first_name.strip()
            
            if last_name is not None:
                user.last_name = last_name.strip()
                updated_fields["last_name"] = last_name.strip()
            
            if email is not None:
                if User.objects.filter(email=email).exclude(pk=user.pk).exists():
                    msg = f"Email {email} is already in use by another customer."
                    logger.error(msg)
                    return HTTPResponses.HTTP_STATUS_CUSTOMER_UPDATE_FAILED(customer.id, msg), None
                
                user.email = email.strip()
                updated_fields["email"] = email.strip()

            if autodeposit is not None:
                customer.config.auto_deposit = autodeposit
                updated_fields["auto_deposit"] = autodeposit
            
            if password is not None:
                user.set_password(password)
                updated_fields["password"] = "UPDATED"  # Avoid logging raw passwords

            if updated_fields:
                user.save()
                logger.info(f"Updated customer {customer.id}: {updated_fields}.")
            else:
                logger.info(f"No updates applied for customer {customer.id}. No parameters provided.")
                return HTTPResponses.HTTP_STATUS_CUSTOMER_UPDATE_NO_CHANGES(customer.id), customer

        except Exception as e:
            msg = f"Failed to update customer {customer.id}: {e}."
            logger.error(f"{msg}\n\nTraceback:\n{traceback.format_exc()}\n")
            return HTTPResponses.HTTP_STATUS_CUSTOMER_UPDATE_FAILED(customer.id, msg), None
        customer.save()
        
        logger.info(f"Customer {customer.id} update successful.")
        return HTTPResponses.HTTP_STATUS_CUSTOMER_UPDATE_SUCCESS(customer.id), customer

    @staticmethod
    @transaction.atomic
    def update_customer_config(card_number: str, update_data: dict, logger: logging.Logger = None) -> tuple[Response, CustomerConfig]:
        """
        Updates multiple fields in the customer's configuration.

        Args:
            card_number (str): The unique customer card number.
            update_data (dict): Dictionary containing fields to update.
            logger (logging.Logger, optional): Logger instance.

        Returns:
            tuple: (JsonResponse, CustomerConfig) - HTTP Response status and updated config instance.
        """
        if logger is None:
            logger = logging.getLogger(__name__)

        logger.info(f"Updating config for customer {card_number} with data: {update_data}")

        try:
            # Get the customer instance
            customer = Customer.objects.get(card_number=card_number)
            config = customer.config

            # Get all valid fields from the model
            valid_fields = {field.name for field in CustomerConfig._meta.get_fields()}

            # Track updated fields
            field_types = {field.name: field for field in CustomerConfig._meta.get_fields()}
            updated_fields = []
            skipped_fields = []

            # Iterate through received data and update valid fields
            for key, value in update_data.items():
                if key in field_types:
                    field = field_types[key]

                    try:
                        # Convert value to the appropriate field type
                        if isinstance(field, (models.BooleanField, models.NullBooleanField)):
                            value = bool(value)
                        elif isinstance(field, models.IntegerField):
                            value = int(value)
                        elif isinstance(field, models.FloatField):
                            value = float(value)
                        elif isinstance(field, models.CharField):
                            value = str(value)
                        elif isinstance(field, models.DateField):
                            value = datetime.strptime(value, "%Y-%m-%d").date()
                        elif isinstance(field, models.DateTimeField):
                            value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
                        else:
                            logger.warning(f"⚠ Skipping field '{key}' - Unsupported data type {type(field)}.")
                            skipped_fields.append(key)
                            continue

                        # Assign the converted value
                        setattr(config, key, value)
                        updated_fields.append(key)

                    except (ValueError, TypeError) as e:
                        logger.warning(f"⚠ Failed to convert '{key}' with value '{value}': {e}")
                        skipped_fields.append(key)
                else:
                    skipped_fields.append(key)

            # Save only if changes were made
            if updated_fields:
                config.save()
                customer.save()
                logger.info(f"Updated fields: {updated_fields} for customer {card_number}."
                            " Config_id updated: {config.id}.")
                _read_conf = CustomerConfig.objects.get(customer=customer)
                logger.debug(f"Updated config: {_read_conf.__dict__}")
            else:
                logger.warning(f"No valid fields to update for customer {card_number}.")

            # Log skipped fields
            if skipped_fields:
                logger.warning(f"Skipped invalid fields: {skipped_fields}")
            logger.info(f"Config update successful for customer {card_number}.")
            return HTTPResponses.HTTP_STATUS_CUSTOMER_UPDATE_SUCCESS(card_number), config

        except Customer.DoesNotExist:
            msg = f"Customer with card number {card_number} not found."
            logger.error(msg)
            return HTTPResponses.HTTP_STATUS_CUSTOMER_NOT_FOUND(card_number), None

        except Exception as e:
            msg = f"Error updating config for customer {card_number}: {e}"
            logger.error(f"{msg}\n\nTraceback:\n{traceback.format_exc()}\n")
            return HTTPResponses.HTTP_STATUS_CUSTOMER_UPDATE_FAILED(card_number, msg), None

    # Private methods
    # =========================================================================================================
    @staticmethod
    @transaction.atomic
    @journal_command()
    def get_or_create_product(ean: str, name: str, resell_price: Decimal, discount: Decimal, logger: logging.Logger, *args, **kwargs) -> tuple[Response, StoreProduct]:
        """
        Get or create a product by EAN, and update its details if it exists.
        """
        # Check if all required fields are present
        if not ean or not name or not resell_price:
            logger.error("Missing required fields for product creation.")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_PRODUCT_CREATE_FAILED(ean, "Missing required fields"))

        if discount < 0 or discount > 100:
            logger.error(f"Invalid discount value for product '{name}': {discount}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_PRODUCT_CREATE_FAILED(ean, f"Invalid discount value: {discount}"))

        if resell_price < 0:
            logger.error(f"Invalid resell price for product '{name}': {resell_price}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_PRODUCT_CREATE_FAILED(ean, f"Invalid resell price: {resell_price}"))

        # Initialize offextractor to None
        offextractor = None
        nutri_facts = {}
           
        try:
            product, created = StoreProduct.objects.get_or_create(ean=ean)
            StoreHelper.update_product_details(product, product_name=name, resell_price=resell_price, discount=discount, 
                                               logger=logger)
            # Assign nutrition facts if available
            if CONFIG.webservice.HAS_INTERNET_ACCESS:
                try:
                # Attempt to create the extractor and fetch nutrition facts
                    offextractor = OFFExtractor(ean)
                    nutri_facts = offextractor.extract()
                except Exception as e:
                    logger.error(f"Error during product creation: {e}. Skipping. (You need to manually add the nutrition facts)")

                logger.info(f"Creating or retrieving product '{name}' with EAN '{ean}' (Resell Price: {resell_price})")

                if nutri_facts:
                    nutri_score = nutri_facts.get("Nutri-Score")
                    energy_kcal = nutri_facts.get("Energy (kcal)")
                    energy_kj = nutri_facts.get("Energy (kJ)")
                    fat = nutri_facts.get("Fat")
                    carbohydrates = nutri_facts.get("Carbohydrates")
                    sugar = nutri_facts.get("Sugar")
                    fiber = nutri_facts.get("Fiber")
                    proteins = nutri_facts.get("Proteins")
                    salt = nutri_facts.get("Salt")
                    product.image_url = nutri_facts.get("Image URL")

                    StoreHelper.update_product_details(product,
                                                nutri_score=nutri_score, 
                                                energy_kcal=energy_kcal, 
                                                energy_kj=energy_kj, 
                                                fat=fat, carbohydrates=carbohydrates,
                                                sugar=sugar, fiber=fiber,
                                                proteins=proteins, salt=salt, 
                                                logger=logger)
            
            
        except Exception as e:
            logger.error(f"Error during product creation: {e}")
            raise HelperException(f"", HTTPResponses.HTTP_STATUS_PRODUCT_CREATE_FAILED(ean, e))

        if created:
            logger.info(f"New product created: {product}")
            return (HTTPResponses.HTTP_STATUS_PRODUCT_CREATE_SUCCESS(ean), product)
        else:
            logger.info(f"Existing product updated: {product}")
            return (HTTPResponses.HTTP_STATUS_PRODUCT_UPDATE_SUCCESS(ean), product)

    
    
    @staticmethod
    @transaction.atomic
    @journal_command()
    def update_product_details(product: StoreProduct,
                                logger: logging.Logger,
                                product_name: str= None, 
                                resell_price: Decimal= None, 
                                discount: Decimal= None, 
                                nutri_score: str = None, 
                                energy_kcal: Decimal = None, 
                                energy_kj: Decimal = None, 
                                fat: Decimal = None, 
                                carbohydrates: Decimal = None,
                                sugar: Decimal = None,
                                fiber: Decimal = None,
                                proteins: Decimal = None,
                                salt: Decimal = None, 
                                *args, **kwargs
                               ):
        """
        """
        logger.debug(f"Updating Product with EAN: {product.ean}.")   
        # check if the product exists
        if not product:
            raise HelperException(f"Product does not exist.", HTTPResponses.HTTP_STATUS_PRODUCT_NOT_FOUND(product.ean))
        
        def assign_value(field, value, astype, product: StoreProduct):
            try:
                if value is None:
                    logger.warning(f"Value for field '{field}' is None. Skipping.")
                    return
                # Convert to the correct type  
                value = astype(value)
                
                if not isinstance(value, astype):
                    logger.error(f"Invalid value for field '{field}': {value}. Expected type: {astype} but got {type(value)}")
                    raise HelperException(f"Invalid value for field '{field}': {value}.",
                                          HTTPResponses.HTTP_STATUS_FIELD_ASSIGNMENT_FAILED(field, type(value), e))
                
                if isinstance(value, Decimal):
                    value = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                

                logger.debug(f"Assigning value for field '{field}': {value}.")
                setattr(product, field, value)
            except Exception as e:
                errstr = f"Failed to convert {field} ({value}) to {astype}: {e}"
                logger.error(errstr)
                raise HelperException(errstr, HTTPResponses.HTTP_STATUS_FIELD_ASSIGNMENT_FAILED(field, type(value), e))
        
        assign_value("name", product_name, str, product)
        assign_value("resell_price", resell_price, Decimal, product)
        discount = Decimal(Decimal(discount)/100)
        assign_value("discount", discount, Decimal, product)
        assign_value("nutri_score", nutri_score, str, product)
        assign_value("energy_kcal", energy_kcal, Decimal, product)
        assign_value("energy_kj", energy_kj, Decimal, product)
        assign_value("fat", fat, Decimal, product)
        assign_value("carbohydrates", carbohydrates, Decimal, product)
        assign_value("sugar", sugar, Decimal, product)
        assign_value("fiber", fiber, Decimal, product)
        assign_value("proteins", proteins, Decimal, product)
        assign_value("salt", salt, Decimal, product)
        product.save()
        return HTTPResponses.HTTP_STATUS_PRODUCT_UPDATE_SUCCESS(product.ean), product




       



    @staticmethod
    @transaction.atomic
    def _customer_add_purchase(customer: Customer, amount: Decimal, quantity: int, product: StoreProduct, logger: logging.Logger, *args, **kwargs) -> tuple[Response, CustomerPurchase]:
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
            

            purchase_entry = CustomerPurchase.objects.create(
                product=product,
                quantity=quantity,
                purchase_price=amount,
                customer=customer,
                customer_balance=customer.balance
            )
            purchase_entry.calculate_profit(logger)
            purchase_entry.save()
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
                raise HelperException(f"Balance mismatch after purchase for customer {customer}. Total Deposits: {total_deposit}, Total Purchases: {total_purchases}, Balance: {customer.balance}", HTTPResponses.HTTP_STATUS_BALANCE_MISMATCH(customer))
        except Exception as e:
            logger.error(f"Failed to validate balance after purchase for customer {customer}: {e}")
            raise HelperException(f"Failed to validate balance after purchase for customer {customer}: {e}.", HTTPResponses.HTTP_STATUS_PURCHASE_FAILED(e))
        
        purchase_entry.order_status = "completed"
        purchase_entry.payment_status = "paid"
        purchase_entry.save()

        return HTTPResponses.HTTP_STATUS_PURCHASE_SUCCESS(customer), purchase_entry
