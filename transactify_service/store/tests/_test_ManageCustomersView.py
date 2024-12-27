
from unittest.mock import patch
from unittest import skip, skipIf

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from store.webmodels.Customer import Customer
from store.webmodels.StoreProduct import StoreProduct
from store.webmodels.CustomerDeposit import CustomerDeposit


from decimal import Decimal
import json
from django.conf import settings
from django.http import HttpResponse



import logging

class ManageCustomersViewTest(TestCase):

    def setUp(self):
        self.logger = logging.getLogger('ManageCustomersViewTest')
        self.logger.info("Setting up ManageCustomersViewTest")
        # Comment 1: Setting up test client and user login
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        # Comment 2: Creating multiple test customers linked to User objects
        balaces = [0.01, 999999, 100.13, 33.89, 0]
        self.customers = [
            Customer.objects.create(
                user=User.objects.create_user(
                    username=f"user{i}",
                    email=f"test{i}@example.com",
                    password="password"
                ),
                card_number=f"CARD{i}",
                balance=balaces[i],
            )
            for i in range(len(balaces))
        ]

    def test_get_all_customers(self):
        # Comment 4: Testing if the view fetches all customers
        response: HttpResponse = self.client.get(reverse('customers'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/manage_customers.html')

        # Comment 5: Checking if all customers and balances are present in the context
        customers_from_context: list[Customer] = response.context['customers']
        self.assertEqual(len(list(customers_from_context)), len(self.customers))

        # Check the balance of each customer
        for i, customer_from_context in enumerate(customers_from_context):
            self.assertEqual(float(customer_from_context.balance), float(self.customers[i].balance))


    @patch('requests.get')
    def test_post_create_customer_with_mocked_api(self, mock_get):
        # Comment 6: Mocking the API response for NFC reading
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'id': 'MOCK_CARD_ID',
            'content': 'MOCK_CONTENT'
        }

        # Comment 7: Testing if a new customer is created successfully
        new_customer_data = {
            'first_name': 'New',
            'last_name': 'Customer',
            'email': 'newcustomer@example.com',
            'balance': 150.0,
        }
        response = self.client.post(
            reverse('customers'),
            data=json.dumps(new_customer_data),
            content_type='application/json'
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

        # Comment 8: Verifying the new customer and associated data in the database
        new_user = User.objects.filter(email='newcustomer@example.com').first()
        self.assertIsNotNone(new_user)
        new_customer = Customer.objects.filter(user=new_user).first()
        self.assertIsNotNone(new_customer)

        # Comment 9: Checking the associated balance and card number
        self.assertEqual(new_customer.balance, 150.0)
        self.assertEqual(new_customer.card_number, 'MOCK_CARD_ID')

        # Check if the initial balance record is created. note that multiple balance records can be created
        initial_deposit = CustomerDeposit.objects.filter(customer=new_customer).first()
        # check if only one deposit record is created
        self.assertIsNotNone(initial_deposit)
        self.assertEqual(CustomerDeposit.objects.filter(customer=new_customer).count(), 1)
        self.assertEqual(initial_deposit.amount, 150.0)

    @patch('requests.get')
    def test_post_create_customer_with_mocked_api_negative_balance(self, mock_get):
        # Comment 6: Mocking the API response for NFC reading
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'id': 'MOCK_CARD_ID',
            'content': 'MOCK_CONTENT'
        }

        # Comment 7: Testing if a new customer is created successfully
        new_customer_data = {
            'first_name': 'New',
            'last_name': 'Customer',
            'email': 'newcustomer@example.com',
            'balance': -150.0,
        }
        response = self.client.post(
            reverse('customers'),
            data=json.dumps(new_customer_data),
            content_type='application/json'
        )

        # Check if the response is successful
        self.assertEqual(response.status_code, 500)

        # Comment 8: Verifying the new customer and associated data in the database
        new_user = User.objects.filter(email='newcustomer@example.com').first()
        self.assertIsNone(new_user)
        new_customer = Customer.objects.filter(user=new_user).first()
        self.assertIsNone(new_customer)
        self.assertEqual(CustomerDeposit.objects.filter(customer=new_customer).count(), 0)


    @patch('requests.get')
    def test_post_create_customer_with_mocked_api_empty(self, mock_get):
        # Comment 10: Mocking API response with empty NFC card data
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'id': '',
            'content': ''
        }

        # Comment 11: Testing creation of a customer with missing NFC data
        new_customer_data = {
            'first_name': 'New',
            'last_name': 'Customer',
            'email': 'newcustomer@example.com',
            'balance': 150.0,
        }
        response = self.client.post(
            reverse('customers'),
            data=json.dumps(new_customer_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 500)

        # Comment 8: Verifying the new customer and associated data in the database
        new_user = User.objects.filter(email='newcustomer@example.com').first()
        self.assertIsNone(new_user)
        new_customer = Customer.objects.filter(user=new_user).first()
        self.assertIsNone(new_customer)
        self.assertEqual(CustomerDeposit.objects.filter(customer=new_customer).count(), 0)


    @patch('requests.get')
    def test_post_create_customer_with_mocked_api_error(self, mock_get):
        # Mocking API response with error code 404
        mock_get.return_value.status_code = 404
        mock_get.return_value.json.return_value = {
            'detail': 'Not found.'
        }

        # Testing creation of a customer with API error response
        new_customer_data = {
            'first_name': 'New',
            'last_name': 'Customer',
            'email': 'newcustomer@example.com',
            'balance': 150.0,
        }
        response = self.client.post(
            reverse('customers'),
            data=json.dumps(new_customer_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 500)

        # Comment 8: Verifying the new customer and associated data in the database
        new_user = User.objects.filter(email='newcustomer@example.com').first()
        self.assertIsNone(new_user)
        new_customer = Customer.objects.filter(user=new_user).first()
        self.assertIsNone(new_customer)
        self.assertEqual(CustomerDeposit.objects.filter(customer=new_customer).count(), 0)


    def test_post_create_customer_missing_fields(self):
        # Comment 14: Testing error handling for missing fields in the request
        incomplete_customer_data = {
            'first_name': 'Incomplete',
            # Missing last_name, email, and balance
        }
        response = self.client.post(
            reverse('customers'),
            data=json.dumps(incomplete_customer_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

        # Comment 8: Verifying the new customer and associated data in the database
        new_user = User.objects.filter(email='newcustomer@example.com').first()
        self.assertIsNone(new_user)
        new_customer = Customer.objects.filter(user=new_user).first()
        self.assertIsNone(new_customer)
        self.assertEqual(CustomerDeposit.objects.filter(customer=new_customer).count(), 0)



