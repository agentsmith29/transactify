import pytest
from unittest import mock
from unittest.mock import patch, MagicMock
from decimal import Decimal
from datetime import datetime

from django.test import TestCase
from django.db import transaction
from store.webmodels.StoreProduct import StoreProduct
from store.helpers.ManageStockHelper import StoreHelper
from store.helpers.Exceptions import HelperException
from transactify_service.settings import CONFIG
import logging

from decimal import Decimal, ROUND_HALF_UP
class TestStoreProductModel(TestCase):
    def setUp(self):
        self.logger = logging.getLogger("test_logger")
        self.ean = "4014400927139"
        self.name = "Test Product"
        self.resell_price = Decimal("10.99")
        self.discount = Decimal("0.10")

    @patch("store.helpers.ManageStockHelper.OFFExtractor")
    def test_create_product_success(self, mock_off_extractor):
        """Test successful creation of a new product."""
        # Mock OFFExtractor response

        with self.assertLogs(self.logger.name, level="INFO") as log:
            mock_off_extractor.return_value.extract.return_value = {
                "Nutri-Score": "A",
                "Energy (kcal)": 200,
                "Energy (kJ)": 840,
                "Fat": 5,
                "Carbohydrates": 30,
                "Sugar": 10,
                "Fiber": 3,
                "Proteins": 7,
                "Salt": 1,
                "Image URL": "http://example.com/image.jpg",
            }

            response, product = StoreHelper.get_or_create_product(
                ean=self.ean,
                name=self.name,
                resell_price=self.resell_price,
                discount=self.discount,
                logger=self.logger,
            )

        # Assertions
        self.assertEqual(product.name, self.name)
        self.assertEqual(product.resell_price, self.resell_price)
        self.assertEqual(product.discount, self.discount)
        self.assertEqual(product.final_price, Decimal("9.89"))  # 10.99 - 10%
        self.assertEqual(response.status_code, 201)

    @patch("store.helpers.ManageStockHelper.OFFExtractor")
    def test_off_extractor_fails(self, mock_off_extractor):
        """Test when OFFExtractor fails to fetch data."""
        # Simulate an exception in OFFExtractor
        mock_off_extractor.side_effect = Exception("OFFExtractor error")

        logger_name = self.logger.name  # Ensure the logger name matches the logger in the function

        with self.assertLogs("test_logger", level="ERROR") as log:
            response, product = StoreHelper.get_or_create_product(
                ean=self.ean,
                name=self.name,
                resell_price=self.resell_price,
                discount=self.discount,
                logger=self.logger,
            )

        # Assertions
        self.assertGreater(len(log.output), 0, "No logs were captured.")
        self.assertTrue(any("Error during product creation" in message for message in log.output))

        # Ensure the product is created with default values for nutrition facts
        self.assertIsNotNone(product)
        self.assertIsNone(product.nutri_score)
        self.assertIsNone(product.energy_kcal)


    def test_missing_required_fields(self):
        """Test missing required fields raises HelperException."""
        with self.assertRaises(HelperException):
            StoreHelper.get_or_create_product(
                ean=None,
                name=self.name,
                resell_price=self.resell_price,
                discount=self.discount,
                logger=self.logger,
            )

    def test_invalid_discount_value(self):
        """Test invalid discount values."""
        invalid_discounts = [-10, 150]

        for discount in invalid_discounts:
            with self.assertRaises(HelperException):
                StoreHelper.get_or_create_product(
                    ean=self.ean,
                    name=self.name,
                    resell_price=self.resell_price,
                    discount=Decimal(discount / 100),
                    logger=self.logger,
                )

    def test_invalid_resell_price(self):
        """Test invalid resell price values."""
        invalid_resell_prices = [-1, -100]

        for price in invalid_resell_prices:
            with self.assertRaises(HelperException):
                StoreHelper.get_or_create_product(
                    ean=self.ean,
                    name=self.name,
                    resell_price=Decimal(price),
                    discount=self.discount,
                    logger=self.logger,
                )

    @patch("store.helpers.ManageStockHelper.OFFExtractor")
    def test_update_existing_product(self, mock_off_extractor):
        """Test updating an existing product."""
        # Mock OFFExtractor response
        mock_off_extractor.return_value.extract.return_value = {
            "Nutri-Score": "B",
            "Energy (kcal)": 150,
            "Energy (kJ)": 600,
            "Fat": 3,
            "Carbohydrates": 20,
            "Sugar": 5,
            "Fiber": 2,
            "Proteins": 10,
            "Salt": 0.5,
            "Image URL": "http://example.com/updated_image.jpg",
        }

        product = StoreProduct.objects.create(
            ean=self.ean, name=self.name, resell_price=self.resell_price, discount=self.discount
        )

        response, updated_product = StoreHelper.get_or_create_product(
            ean=self.ean,
            name="Updated Product",
            resell_price=Decimal("12.99"),
            discount=Decimal("0.05"),
            logger=self.logger,
        )

        # Assertions
        self.assertEqual(updated_product.name, "Updated Product")
        self.assertEqual(updated_product.resell_price, Decimal("12.99"))
        self.assertEqual(updated_product.discount, Decimal("0.05"))
        self.assertEqual(response.status_code, 200)

    @patch("store.helpers.ManageStockHelper.CONFIG")
    def test_journal_command(self, mock_config):
        """Test the journal_command wrapper."""
        mock_config.webservice.JOURNAL_FILE = "/tmp/test_journal.log"

        with patch("builtins.open", mock.mock_open()) as mocked_file:
            StoreHelper.get_or_create_product(
                ean=self.ean,
                name=self.name,
                resell_price=self.resell_price,
                discount=self.discount,
                logger=self.logger,
            )

            mocked_file.assert_called_once_with(mock_config.webservice.JOURNAL_FILE, "a")

    def test_calculate_final_price(self):
        """Test final price calculation."""
        discount = Decimal("0.10")
        resell_price = Decimal("10.99")
        final_price = Decimal(resell_price - (resell_price * discount))
        final_price = final_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        product = StoreProduct(
            ean=self.ean, resell_price=resell_price, discount=discount
        )
        self.assertEqual(product.calculate_final_price(), final_price)  # 10.99 - 10%

    def test_calculate_final_price_in_precent(self):
        """Test final price calculation."""
        discount = Decimal(11)
        resell_price = Decimal("10.99")        
        product = StoreProduct(
            ean=self.ean, resell_price=resell_price, discount=discount
        )
        # CHeck for ValueError on calculate_final_price
        with self.assertRaises(ValueError):
            product.calculate_final_price()


    def test_save_updates_final_price(self):
        """Test the save method updates final_price correctly."""
        product = StoreProduct(
            ean=self.ean, name=self.name, resell_price=self.resell_price, discount=self.discount
        )
        product.save()
        self.assertEqual(product.final_price, Decimal("9.89"))

    def test_get_top_selling_products(self):
        """Test fetching top-selling products."""
        StoreProduct.objects.bulk_create(
            [
                StoreProduct(ean="1", name="Product 1", total_orders=50, total_revenue=Decimal("500.00")),
                StoreProduct(ean="2", name="Product 2", total_orders=30, total_revenue=Decimal("300.00")),
                StoreProduct(ean="3", name="Product 3", total_orders=10, total_revenue=Decimal("100.00")),
            ]
        )

        top_products = StoreProduct.get_top_selling_products(limit=2)
        self.assertEqual(len(top_products), 2)
        self.assertEqual(top_products[0]["name"], "Product 1")
        self.assertEqual(top_products[1]["name"], "Product 2")
