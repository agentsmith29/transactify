import pytest
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from store.webmodels.StoreProduct import StoreProduct
from store.webmodels.StoreCashMovement import StoreCashMovement
from store.webmodels.ProductRestock import ProductRestock
from store.helpers.ManageStockHelper import StoreHelper
from store.webmodels.StoreCash import StoreCash
from django.utils import timezone

from store.helpers.Exceptions import HelperException
import logging

class TestRestockProduct(TestCase):
    def setUp(self):
        self.logger = logging.getLogger(TestRestockProduct.__name__)
        self.logger.setLevel(logging.DEBUG)
        self.auth_user = User.objects.create(username="test_user")
        self.ean = "4014400927139"
        self.name = "Test Product"
        self.resell_price = Decimal("10.99")
        self.purchase_price = Decimal("5.00")
        self.discount = Decimal("0.10")
        self.quantity = 10

        # Create the product for testing
        response, self.product = StoreHelper.get_or_create_product(
            ean=self.ean,
            name=self.name,
            resell_price=self.resell_price,
            discount=self.discount,
            logger=self.logger,
        )

    def test_successful_restock_with_equity(self):
        """Test successful restock with store equity."""
        initial_stock = StoreHelper.get_stock_quantity(self.product, self.logger)

        # Add some store equity
        StoreCash.objects.create(
            cash=Decimal("1000.00"),
            last_updated=timezone.now(),
            )

        # Perform the restock
        response, product_restock = StoreHelper.restock_product(
            ean=self.ean,
            quantity=self.quantity,
            purchase_price=self.purchase_price,
            auth_user=self.auth_user,
            logger=self.logger,
            used_store_equity=True,
        )

        # Assertions
        self.product.refresh_from_db()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.product.stock_quantity, initial_stock + self.quantity)  # Updated stock
        self.assertEqual(product_restock.quantity, self.quantity)

        # Verify the cash movement record
        cash_movement = StoreCashMovement.objects.filter(amount=self.purchase_price * self.quantity).first()
        self.assertIsNotNone(cash_movement)
        self.assertEqual(cash_movement.movement_type, "withdraw")

    def test_restock_with_equty_insufficient_funds(self):
        """Test restocking with insufficient store equity."""
        initial_stock = StoreHelper.get_stock_quantity(self.product, self.logger)

        # Perform the restock
        with self.assertLogs(self.logger.name, level="ERROR") as log:
            with self.assertRaises(HelperException):
                StoreHelper.restock_product(
                    ean=self.ean,
                    quantity=self.quantity,
                    purchase_price=self.purchase_price,
                    auth_user=self.auth_user,
                    logger=self.logger,
                    used_store_equity=True,
                )

        # Assertions
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, initial_stock)


    def test_successful_restock_with_cash_deposit(self):
        """Test successful restock with cash deposit."""
        initial_stock = StoreHelper.get_stock_quantity(self.product, self.logger)

        # Perform the restock
        response, product_restock = StoreHelper.restock_product(
            ean=self.ean,
            quantity=self.quantity,
            purchase_price=self.purchase_price,
            auth_user=self.auth_user,
            logger=self.logger,
            used_store_equity=False,
        )

        # Assertions
        self.product.refresh_from_db()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.product.stock_quantity, initial_stock + self.quantity)  # Updated stock
        self.assertEqual(product_restock.quantity, self.quantity)

        # Verify the cash movement record
        cash_movement = StoreCashMovement.objects.filter(amount=self.purchase_price * self.quantity).first()
        self.assertIsNotNone(cash_movement)
        self.assertEqual(cash_movement.movement_type, "deposit")

    def test_product_does_not_exist(self):
        """Test restocking a non-existent product."""
        invalid_ean = "9999999999999"

        with self.assertLogs(self.logger.name, level="ERROR") as log:
            with self.assertRaises(HelperException):
                StoreHelper.restock_product(
                    ean=invalid_ean,
                    quantity=self.quantity,
                    purchase_price=self.purchase_price,
                    auth_user=self.auth_user,
                    logger=self.logger,
                )

        # Assert the error log message was captured
        self.assertTrue(any(f"Product with EAN {invalid_ean} does not exist." in message for message in log.output))

    def test_cash_movement_failure(self):
        """Test failure during cash movement creation."""
        # Intentionally set an invalid amount to cause a failure
        invalid_purchase_price = Decimal("-1.00")

        with self.assertLogs(self.logger.name, level="ERROR") as log:
            with self.assertRaises(HelperException):
                StoreHelper.restock_product(
                    ean=self.ean,
                    quantity=self.quantity,
                    purchase_price=invalid_purchase_price,
                    auth_user=self.auth_user,
                    logger=self.logger,
                )

        # Assert the error log message was captured
        self.assertTrue(any("Cannot create StoreCashWithdraw" in message for message in log.output))

    def test_atomic_transaction_rollback_on_failure(self):
        """Test that transaction rolls back on failure."""
        initial_stock = self.product.stock_quantity

        with self.assertLogs(self.logger.name, level="ERROR") as log:
            with self.assertRaises(HelperException):
                # Simulate failure during restock by using invalid quantity
                StoreHelper.restock_product(
                    ean=self.ean,
                    quantity=-10,  # Invalid quantity
                    purchase_price=self.purchase_price,
                    auth_user=self.auth_user,
                    logger=self.logger,
                )

        # Ensure the product stock quantity is not updated
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, initial_stock)  # Stock remains unchanged

        # Assert the rollback was logged
        self.assertTrue(any("Invalid restock quantity" in message for message in log.output))

    def test_create_product_and_restock(self):
        """Test creating a product and then restocking it."""
        new_ean = "1234567890123"
        new_name = "New Product"
        new_resell_price = Decimal("15.99")
        new_purchase_price = Decimal("7.50")
        new_quantity = 20

        # Create a new product
        response, product = StoreHelper.get_or_create_product(
            ean=new_ean,
            name=new_name,
            resell_price=new_resell_price,
            discount=self.discount,
            logger=self.logger,
        )

        # Assertions for product creation
        self.assertEqual(response.status_code, 201)
        self.assertEqual(product.name, new_name)

        # Restock the newly created product
        response, product_restock = StoreHelper.restock_product(
            ean=new_ean,
            quantity=new_quantity,
            purchase_price=new_purchase_price,
            auth_user=self.auth_user,
            logger=self.logger,
            used_store_equity=False,
        )

        # Assertions for restocking
        product.refresh_from_db()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(product.stock_quantity, new_quantity)
        self.assertEqual(product_restock.quantity, new_quantity)

        # Verify the cash movement record
        cash_movement = StoreCashMovement.objects.filter(amount=new_purchase_price * new_quantity).first()
        self.assertIsNotNone(cash_movement)
        self.assertEqual(cash_movement.movement_type, "deposit")
