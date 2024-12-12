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
            stores (list[Store]): List of Store objects containing API base URLs.
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

                # Validate response data
                if not all(key in product_data for key in ['ean', 'name', 'stock_quantity', 'discount', 'resell_price', 'final_price']):
                    # Change No. #1: Ensure all required keys are present in the response.
                    print(f"Invalid data structure from API response at {store.address}")
                    continue

                # Create an instance of StoreProduct with the fetched data
                return cls(
                    store=store,
                    ean=product_data.get('ean'),
                    name=product_data.get('name'),
                    stock_quantity=product_data.get('stock_quantity'),
                    discount=Decimal(product_data.get('discount', 0)),  # Change No. #2: Ensure Decimal conversion for numeric values.
                    resell_price=Decimal(product_data.get('resell_price', 0)),
                    final_price=Decimal(product_data.get('final_price', 0)),
                )
            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch product from {store}: {e}")
                traceback.print_exc()
            except KeyError as e:
                print(f"Missing expected key in API response from {store}: {e}")
            except Exception as e:
                print(f"Unexpected error when fetching product from {store}: {e}")
                traceback.print_exc()
        return None  # Return None if no product is found

    def customer_purchase(self, customer: Customer, quantity=1) -> Response:
        """
        Calls the customer_purchase API endpoint.

        Args:
            customer (Customer): Customer object performing the purchase.
            quantity (int): The quantity to purchase.

        Returns:
            Response: The API response object.

        Raises:
            Exception: If the API call fails or returns an error.
        """
        if not isinstance(quantity, int) or quantity <= 0:
            # Change No. #3: Validate quantity input.
            raise ValueError("Quantity must be a positive integer.")

        payload = {
            "ean": self.ean,
            "quantity": quantity,
            "card_number": customer.card_number,
        }
        headers = {
            "Content-Type": "application/json"
        }
        print(f"Making purchase: {payload}")
        try:
            api_url = f"http://{self.store.address}/api/purchase/"
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        except requests.exceptions.RequestException as e:
            print(f"Failed to make purchase: {e}")
            traceback.print_exc()
            return Response(status=response.status_code if response else 500, 
                            text=f"API request failed: {e}")  # Change No. #4: Ensure a proper response is returned even on failure.
        except Exception as e:
            print(f"Unexpected error during purchase: {e}")
            traceback.print_exc()
            return Response(status=500, text=f"Unexpected error: {e}")

        return response
