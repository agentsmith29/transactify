import requests
from django.http import JsonResponse

import requests

from ..controller.ConfParser import Store
from decimal import Decimal

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
    def get_from_api(cls, store: Store, card_number):
        """
        Fetch a customer from multiple base URLs based on EAN.
        Args:
            base_urls (list): List of API base URLs.
            ean (str): Product EAN code.
        Returns:
            StoreProduct instance if product is found; otherwise None.
    """
        try:
            # Construct the API URL
            api_url = f"http://{store.address}/api/customers/{card_number}/?format=json"
            # Fetch product details
            response = requests.get(api_url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            product_data = response.json()
            # Create an instance of StoreProduct with the fetched data
            return cls(
                store=store,
                username=product_data.get('username'),
                first_name=product_data.get('first_name'),
                last_name=product_data.get('last_name'),
                email=product_data.get('email'),
                card_number=product_data.get('card_number'),
                issued_at=product_data.get('issued_at'),
                balance=product_data.get('balance'),
                total_deposits=product_data.get('total_deposits'),
                total_purchases=product_data.get('total_purchases'),
                last_changed=product_data.get('last_changed')
            )
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch customer from {store}: {e}")
        except KeyError as e:
            print(f"Missing expected key in API response from {store}: {e}")
        return None  # Return None if no product is found