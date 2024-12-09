import requests
from django.http import JsonResponse

import requests
import traceback

from ..controller.ConfParser import Store
from decimal import Decimal
from ..api_endpoints.Customer import Customer

from requests.models import Response

class StoreProduct:
    def __init__(self, store: Store, ean: str, name: str, stock_quantity: int, discount: Decimal, resell_price: Decimal, final_price: Decimal):
        self.store = store
        self.ean = ean
        self.name = name
        self.stock_quantity = stock_quantity
        self.discount = discount
        self.resell_price = resell_price
        self.final_price = final_price

    @classmethod
    def get_from_api(cls, stores: list[Store], ean):
        """
        Fetch a product from multiple base URLs based on EAN.
        Args:
            base_urls (list): List of API base URLs.
            ean (str): Product EAN code.
        Returns:
            StoreProduct instance if product is found; otherwise None.
        """
        for store in stores:
            try:
                # Construct the API URL
                api_url = f"http://{store.address}/api/products/{ean}/?format=json"
                # Fetch product details
                response = requests.get(api_url)
                response.raise_for_status()  # Raise an exception for HTTP errors

                product_data = response.json()
                # Create an instance of StoreProduct with the fetched data
                return cls(
                    store=store,
                    ean=product_data.get('ean'),
                    name=product_data.get('name'),
                    stock_quantity=product_data.get('stock_quantity'),
                    discount=product_data.get('discount'),
                    resell_price=product_data.get('resell_price'),
                    final_price=product_data.get('final_price'),
                )
            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch product from {store}: {e}")
            except KeyError as e:
                print(f"Missing expected key in API response from {store}: {e}")
        return None  # Return None if no product is found
    
    def customer_purchase(self, customer: Customer, quantity=1) -> Response:
        """
        Calls the customer_purchase API endpoint.

        Args:
            api_url (str): The full URL to the API endpoint (e.g., "http://localhost:8000/api/purchase/").
            ean (str): The EAN of the product.
            quantity (int): The quantity to purchase.
            sale_price (Decimal): The sale price of the product.
            card_number (str): The customer identifier.

        Returns:
            dict: A dictionary containing the API response.

        Raises:
            Exception: If the API call fails or returns an error.
        """
        payload = {
            "ean": self.ean,
            "quantity": quantity,
            "card_number": customer.card_number,
        }

        try:
            api_url = f"http://{self.store.address}/api/purchase/"
            response = requests.post(api_url, json=payload)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            return 0
        except Exception as e:
            print(f"Failed to make purchase: {e}")
            traceback.print_exc()
            return response
