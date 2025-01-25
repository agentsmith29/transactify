from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from store.webmodels.Customer import Customer
from store.webmodels.CustomerDeposit import CustomerDeposit
from store.helpers.ManageStockHelper import StoreHelper
from store.helpers.Exceptions import HelperException
import logging
from django.utils import timezone

class TestCustomerAddDeposit(TestCase):
    def setUp(self):
        self.logger = logging.getLogger("TestCustomerAddDeposit")
        self.logger.setLevel(logging.DEBUG)

        # Create a test customer
        self.user = User.objects.create_user(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com"
        )
        self.customer = Customer.objects.create(
            user=self.user,
            card_number="1234567890",
            balance=Decimal("100.00"),
            total_deposits=0
        )

        CustomerDeposit.objects.create(
            customer=self.customer,
            amount=Decimal("100.00"),
            customer_balance=Decimal("100.00"),
            deposit_date = timezone.now()
        )


    def test_add_positive_deposit(self):
        """Test adding a positive deposit to the customer."""
        response, deposit_entry = StoreHelper.customer_add_deposit(self.customer, Decimal("50.00"), self.logger)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.customer.balance, Decimal("150.00"))
        self.assertEqual(self.customer.total_deposits, 1)
        self.assertEqual(deposit_entry.amount, Decimal("50.00"))
        self.assertEqual(deposit_entry.customer_balance, Decimal("150.00"))

    def test_add_zero_deposit(self):
        """Test adding a deposit of zero, which should raise an error."""
        with self.assertRaises(HelperException):
            StoreHelper.customer_add_deposit(self.customer, Decimal("0.00"), self.logger)

    def test_add_negative_deposit(self):
        """Test adding a negative deposit, which should raise an error."""
        with self.assertRaises(HelperException):
            StoreHelper.customer_add_deposit(self.customer, Decimal("-50.00"), self.logger)

    def test_add_large_deposit(self):
        """Test adding a large deposit to ensure proper handling."""
        large_amount = Decimal("9999999.99")
        response, deposit_entry = StoreHelper.customer_add_deposit(self.customer, large_amount, self.logger)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.customer.balance, Decimal("100.00") + large_amount)
        self.assertEqual(self.customer.total_deposits, 1)
        self.assertEqual(deposit_entry.amount, large_amount)
        self.assertEqual(deposit_entry.customer_balance, Decimal("100.00") + large_amount)

    def test_add_multiple_deposits(self):
        """Test adding multiple deposits consecutively."""
        response1, deposit1 = StoreHelper.customer_add_deposit(self.customer, Decimal("50.00"), self.logger)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(self.customer.balance, Decimal("150.00"))
        self.assertEqual(self.customer.total_deposits, 1)

        response2, deposit2 = StoreHelper.customer_add_deposit(self.customer, Decimal("25.00"), self.logger)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(self.customer.balance, Decimal("175.00"))
        self.assertEqual(self.customer.total_deposits, 2)

    def test_balance_mismatch_after_deposit(self):
        """Test that a balance mismatch raises an error."""
        # Manually modify the customer's balance to simulate a mismatch
        self.customer.balance = Decimal("50.00")
        self.customer.save()

        with self.assertRaises(HelperException):
            StoreHelper.customer_add_deposit(self.customer, Decimal("100.00"), self.logger)

    def test_database_integrity_on_failure(self):
        """Test that database remains consistent when an exception is raised."""
        with self.assertRaises(HelperException):
            StoreHelper.customer_add_deposit(self.customer, Decimal("-50.00"), self.logger)

        # Ensure the balance and deposits remain unchanged
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.balance, Decimal("100.00"))
        self.assertEqual(self.customer.total_deposits, 0)

    def test_deposit_logging(self):
        """Test that deposits are correctly logged."""
        with self.assertLogs(self.logger.name, level="INFO") as log:
            response, deposit_entry = StoreHelper.customer_add_deposit(self.customer, Decimal("50.00"), self.logger)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(any("Adding deposit for customer" in message for message in log.output))
        self.assertTrue(any("Updated balance for customer" in message for message in log.output))
        self.assertTrue(any("Logged deposit for customer" in message for message in log.output))

    def test_add_deposit_with_invalid_decimal(self):
        """Test adding a deposit with an invalid decimal format."""
        with self.assertRaises(HelperException):
            StoreHelper.customer_add_deposit(self.customer, "invalid_decimal", self.logger)

    def test_edge_case_rounding(self):
        """Test that amounts are properly rounded to two decimal places."""
        response, deposit_entry = StoreHelper.customer_add_deposit(self.customer, Decimal("50.005"), self.logger)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(deposit_entry.amount, Decimal("50.01"))  # Rounded to two decimal places
        self.assertEqual(self.customer.balance, Decimal("150.01"))

    def test_add_deposit_with_high_precision_decimal(self):
        """Test adding a deposit with high precision decimal values."""
        high_precision_amount = Decimal("50.123456789")
        response, deposit_entry = StoreHelper.customer_add_deposit(self.customer, high_precision_amount, self.logger)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(deposit_entry.amount, Decimal("50.12"))  # Rounded to two decimal places
        self.assertEqual(self.customer.balance, Decimal("150.12"))

    def test_customer_without_existing_deposit(self):
        """Test adding a deposit to a customer who has no prior deposits."""
        self.assertEqual(self.customer.total_deposits, 0)  # Ensure no deposits initially
        response, deposit_entry = StoreHelper.customer_add_deposit(self.customer, Decimal("100.00"), self.logger)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.customer.total_deposits, 1)
        self.assertEqual(self.customer.balance, Decimal("200.00"))
