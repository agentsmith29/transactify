from django.http import JsonResponse
import requests
from rest_framework.response import Response

from terminal.webmodels.Store import Store
from decimal import Decimal

from .APIFetchException import APIFetchException
from .APIBaseClass import APIBaseClass
import traceback
import logging
from transactify_terminal.settings import CONFIG

class Customer():
    
    def __init__(self, store: Store,
                    username: str, first_name: str, last_name: str, email: str,
                    card_number: str, issued_at: str, balance: Decimal,
                    total_deposits: Decimal, total_purchases: Decimal, last_changed: str):
        super().__init__()

        self.store = store
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.card_number = card_number
        self.issued_at = issued_at
        self.balance = balance
        self.total_deposits = total_deposits
        self.total_purchases = total_purchases
        self.last_changed = last_changed

    @classmethod
    def get_from_api(cls, store: Store, card_number: str, logger: logging.Logger = None):
        """
        Fetch a customer from multiple base URLs based on EAN.
        Args:
            base_urls (list): List of API base URLs.
            ean (str): Product EAN code.
        Returns:
            StoreProduct instance if product is found; otherwise None.
        """
        logger = logging.getLogger(f"{CONFIG.webservice.SERVICE_NAME}.{cls.__class__.__name__}")  
        if card_number is None or card_number == "":
            logger.error("Card number cannot be empty.")
            raise ValueError("Card number cannot be empty.")

        try:
            api_url = f"{store.web_address}/api/customers/{card_number}/?format=json"
            logger.debug(f"Fetching customer data API: {api_url}")
            # Fetch product details using the rest framework request object
            response = requests.get(api_url)
            logger.debug(f"API response recieved: {response}")
            response.raise_for_status()  # Raise an exception for HTTP errors

            customer_data = response.json()
            user = customer_data.get("user", {})
            return cls(
                store=store,
                username=user.get("username"),
                first_name=user.get("first_name"),
                last_name=user.get("last_name"),
                email=user.get("email"),
                card_number=customer_data.get("card_number"),
                issued_at=customer_data.get("issued_at"),
                balance=customer_data.get("balance"),
                total_deposits=customer_data.get("total_deposits"),
                total_purchases=customer_data.get("total_purchases"),
                last_changed=customer_data.get("last_changed"),
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in Line {traceback.extract_stack(None, 2)[0].lineno}, File {traceback.extract_stack(None, 2)[0].filename}:\n"
                         f"Unexpected error during purchase: {e}")
            #print(traceback.format_exc())
            raise e
        except KeyError as e:
            logger.error(f"Missing expected key in API response from {store}: {e}")
            #print(traceback.format_exc())
            raise e
        except Exception as e:
            logger.error(f"Error during API fetch: {e}")
            #print(traceback.format_exc())
            raise e
        
        return response, None  # Return None if no product is found