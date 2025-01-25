from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User, Group
from store.webmodels.Customer import Customer
from store.helpers.ManageStockHelper import StoreHelper
from store.helpers.Exceptions import HelperException
import logging

class TestCreateNewCustomer(TestCase):
    def setUp(self):
        self.logger = logging.getLogger("TestCreateNewCustomer")
        self.logger.setLevel(logging.DEBUG)

    def test_successful_customer_creation_with_deposit(self):
        """Test successful creation of a new customer with a deposit."""
        response, customer = StoreHelper.create_new_customer(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            balance=Decimal("100.00"),
            card_number="1234567890",
            logger=self.logger,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(customer.user.username, "testuser")
        self.assertEqual(customer.balance, Decimal("100.00"))
        self.assertEqual(customer.total_deposits, 1)

    def test_customer_creation_without_deposit(self):
        """Test successful creation of a new customer without an initial deposit."""
        response, customer = StoreHelper.create_new_customer(
            username="nodeposit",
            first_name="No",
            last_name="Deposit",
            email="nodeposit@example.com",
            balance=Decimal("0.00"),
            card_number="0987654321",
            logger=self.logger,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(customer.user.username, "nodeposit")
        self.assertEqual(customer.balance, Decimal("0.00"))
        self.assertEqual(customer.total_deposits, 0)

    def test_duplicate_card_number(self):
        """Test that creating a customer with a duplicate card number raises an error."""
        StoreHelper.create_new_customer(
            username="duplicate",
            first_name="Duplicate",
            last_name="Test",
            email="duplicate@example.com",
            balance=Decimal("50.00"),
            card_number="1234567890",
            logger=self.logger,
        )
        with self.assertRaises(HelperException):
            StoreHelper.create_new_customer(
                username="duplicate2",
                first_name="Duplicate",
                last_name="Test2",
                email="duplicate2@example.com",
                balance=Decimal("50.00"),
                card_number="1234567890",  # Same card number
                logger=self.logger,
            )

    def test_negative_balance(self):
        """Test that creating a customer with a negative balance raises an error."""
        with self.assertRaises(HelperException):
            StoreHelper.create_new_customer(
                username="negativebalance",
                first_name="Negative",
                last_name="Balance",
                email="negative@example.com",
                balance=Decimal("-10.00"),  # Negative balance
                card_number="9876543210",
                logger=self.logger,
            )

    def test_invalid_card_number(self):
        """Test that creating a customer with an invalid card number raises an error."""
        with self.assertRaises(HelperException):
            StoreHelper.create_new_customer(
                username="invalidcard",
                first_name="Invalid",
                last_name="Card",
                email="invalid@example.com",
                balance=Decimal("50.00"),
                card_number="",  # Empty card number
                logger=self.logger,
            )

    def test_customer_add_deposit(self):
        """Test adding a deposit to an existing customer."""
        response, customer = StoreHelper.create_new_customer(
            username="testdeposit",
            first_name="Test",
            last_name="Deposit",
            email="deposit@example.com",
            balance=Decimal("0.00"),
            card_number="1122334455",
            logger=self.logger,
        )
        self.assertEqual(customer.balance, Decimal("0.00"))

        # Add deposit
        response, deposit_entry = StoreHelper.customer_add_deposit(customer, Decimal("200.00"), self.logger)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(customer.balance, Decimal("200.00"))
        self.assertEqual(customer.total_deposits, 1)
