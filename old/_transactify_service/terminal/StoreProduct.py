import requests
from django.http import JsonResponse

import requests

class StoreProduct:
    def __init__(self, base, ean, name, stock_quantity, discount, resell_price, final_price):
        self.base = base
        self.ean = ean
        self.name = name
        self.stock_quantity = stock_quantity
        self.discount = discount
        self.resell_price = resell_price
        self.final_price = final_price

    @classmethod
    def get_product_from_api(cls, base_urls, ean):
        """
        Fetch a product from multiple base URLs based on EAN.
        Args:
            base_urls (list): List of API base URLs.
            ean (str): Product EAN code.
        Returns:
            StoreProduct instance if product is found; otherwise None.
        """
        for base in base_urls:
            try:
                # Construct the API URL
                api_url = f"{base}/api/products/{ean}/?format=json"
                # Fetch product details
                response = requests.get(api_url)
                response.raise_for_status()  # Raise an exception for HTTP errors

                product_data = response.json()
                # Create an instance of StoreProduct with the fetched data
                return cls(
                    base=base,
                    ean=product_data.get('ean'),
                    name=product_data.get('name'),
                    stock_quantity=product_data.get('stock_quantity'),
                    discount=product_data.get('discount'),
                    resell_price=product_data.get('resell_price'),
                    final_price=product_data.get('final_price'),
                )
            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch product from {base}: {e}")
            except KeyError as e:
                print(f"Missing expected key in API response from {base}: {e}")
        return None  # Return None if no product is found

    @staticmethod
    def get_product_list(base_url):
        """
        Fetch a list of products from a specific API base URL.
        Args:
            base_url (str): API base URL.
        Returns:
            list: A list of product dictionaries or an empty list if the request fails.
        """
        try:
            api_url = f"{base_url}/api/products/?format=json"
            response = requests.get(api_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch product list from {base_url}: {e}")
            return []
