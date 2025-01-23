import requests
from django.http import JsonResponse

import traceback

from terminal.webmodels.Store import Store
from decimal import Decimal
from .APIFetchCustomer import Customer

from requests.models import Response
from terminal.api_endpoints.APIFetchException import APIFetchException
from rest_framework import status
from rest_framework.request import Request

from .APIBaseClass import APIBaseClass
import logging
from transactify_terminal.settings import CONFIG

class APIFetchStoreProduct():
    def __init__(self, store: Store, ean: str, name: str, stock_quantity: int, discount: Decimal, resell_price: Decimal, final_price: Decimal):
        super().__init__()
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
        logger = logging.getLogger(f"{CONFIG.webservice.SERVICE_NAME}.{cls.__class__.__name__}")  
        if ean is None or ean == "":
            logger.error("EAN cannot be empty.")
            raise ValueError("EAN cannot be empty.")
       
        for storenum, store in enumerate(stores):
            logger.info(f"({storenum}/{len(stores)}) Fetching product from {store}")
            try:
                # Construct the API URL
                api_url = f"{store.web_address}/api/products/{ean}/?format=json"
                logger.debug(f"Fetching product data API: {api_url}")
                # Fetch product details
                response = requests.get(api_url)
                logger.debug(f"API response recieved: {response}")
                response.raise_for_status()  # Raise an exception for HTTP errors

                product_data = response.json()

                # Validate response data
                if not all(key in product_data for key in ['ean', 'name', 'stock_quantity', 'discount', 'resell_price', 'final_price']):
                    # Change No. #1: Ensure all required keys are present in the response.
                    logger.warning(f"Invalid data structure from API response at {store.web_address}")
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
                logger.error(f"Failed to fetch product from {store}: {e}")
                traceback.print_exc()
            except KeyError as e:
                logger.error(f"Missing expected key in API response from {store}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error when fetching product from {store}: {e}")
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
        except Exception as e:
            print(f"Unexpected error during purchase: {e}")
            tb = traceback.format_exc()
            raise APIFetchException("Failed to make purchase", e, response, tb)
        return response
