from django.http import JsonResponse
import requests
from rest_framework.response import Response

from ..controller.ConfParser import Store
from decimal import Decimal

from ..api_endpoints.APIFetchException import APIFetchException
import traceback
import logging

class Customer:
    
    def __init__(self, store: Store,
                    username: str, first_name: str, last_name: str, email: str,
                    card_number: str, issued_at: str, balance: Decimal,
                    total_deposits: Decimal, total_purchases: Decimal, last_changed: str):
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
    def get_from_api(cls, store: Store, card_number: str):
        """
        Fetch a customer from multiple base URLs based on EAN.
        Args:
            base_urls (list): List of API base URLs.
            ean (str): Product EAN code.
        Returns:
            StoreProduct instance if product is found; otherwise None.
        """
        if card_number is None or card_number == "":
            raise ValueError("Card number cannot be empty.")
        
        logger = logging.getLogger("Customer")
        try:
            logger.info(f"Fetching customer data for card number {card_number} from {store}.")
            
            # Construct the API URL
            api_url = f"http://{store.address}/api/customers/{card_number}/?format=json"
            logger.info(f"Requesting API: `{api_url}`")
            # Fetch product details using the rest framework request object
            response = requests.get(api_url)
            print(f"*** Response: {response}")
            import time; time.sleep(1)
            response.raise_for_status()  # Raise an exception for HTTP errors

            product_data = response.json()
            user = product_data.get("user", {})
            balance = product_data.get("balance", {})

            return cls(
                store=store,
                username=user.get("username"),
                first_name=user.get("first_name"),
                last_name=user.get("last_name"),
                email=user.get("email"),
                card_number=product_data.get("card_number"),
                issued_at=product_data.get("issued_at"),
                balance=balance.get("balance"),
                total_deposits=balance.get("total_deposits"),
                total_purchases=balance.get("total_purchases"),
                last_changed=balance.get("last_changed"),
            )
        except requests.exceptions.RequestException as e:
            print(f"Unexpected error during purchase: {e}")
            print(traceback.format_exc())
            raise e
        except KeyError as e:
            print(f"Missing expected key in API response from {store}: {e}")
            print(traceback.format_exc())
            raise e
        
        return response, None  # Return None if no product is found