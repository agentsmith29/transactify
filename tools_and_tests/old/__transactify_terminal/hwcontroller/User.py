import requests
from django.http import JsonResponse

import requests

import requests


class Customer:
    def __init__(self, base, id, username, first_name, last_name, email, card_number, issued_at, balance):
        self.base = base
        self.id = id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.card_number = card_number
        self.issued_at = issued_at
        self.balance = balance

    @classmethod
    def get_customer_from_api(cls, base_urls, customer_id):
        """
        Fetch a customer from multiple base URLs based on customer ID.
        Args:
            base_urls (list): List of API base URLs.
            customer_id (int or str): Customer ID or card number.
        Returns:
            Customer instance if customer is found; otherwise None.
        """
        for base in base_urls:
            try:
                # Construct the API URL
                api_url = f"{base}/api/customers/{customer_id}/?format=json"
                # Fetch customer details
                response = requests.get(api_url)
                response.raise_for_status()  # Raise an exception for HTTP errors

                customer_data = response.json()
                # Create an instance of Customer with the fetched data
                return cls(
                    base=base,
                    id=customer_data.get('id'),
                    username=customer_data.get('username'),
                    first_name=customer_data.get('first_name'),
                    last_name=customer_data.get('last_name'),
                    email=customer_data.get('email'),
                    card_number=customer_data.get('card_number'),
                    issued_at=customer_data.get('issued_at'),
                    balance=customer_data.get('balance'),
                )
            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch customer from {base}: {e}")
            except KeyError as e:
                print(f"Missing expected key in API response from {base}: {e}")
        return None  # Return None if no customer is found

    @staticmethod
    def get_customer_list(base_url):
        """
        Fetch a list of customers from a specific API base URL.
        Args:
            base_url (str): API base URL.
        Returns:
            list: A list of customer dictionaries or an empty list if the request fails.
        """
        try:
            api_url = f"{base_url}/api/customers/?format=json"
            response = requests.get(api_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch customer list from {base_url}: {e}")
            return []
