from decimal import Decimal
from django.test import TestCase
from store.webmodels.Customer import Customer
from store.webmodels.StoreProduct import StoreProduct
from store.webmodels.ProductRestock import ProductRestock
from store.webmodels.CustomerPurchase import CustomerPurchase
from store.webmodels.ProductInventory import ProductInventory
from django.contrib.auth.models import User
from store.helpers.ManageStockHelper import StoreHelper
import logging
from django.db import models

class TestRestockAndPurchase(TestCase):
    def setUp(self):
        """Setup multiple users, products, and restocks."""
        self.logger = logging.getLogger("TestRestockAndPurchase")
        self.logger.setLevel(logging.INFO)
        
        # Create admin user
        self.admin = User.objects.get_or_create(username="admin")[0]

        # Create customers
        self.customers = []
        for i in range(1, 4):  # 3 customers
            _, customer = StoreHelper.create_new_customer(
                username=f"testuser{i}",
                first_name=f"Test{i}",
                last_name="User",
                email=f"test{i}@test.com",
                balance=Decimal("200.00"),
                card_number=f"12345678901234{i}",
                logger=self.logger
            )
            self.customers.append(customer)

        # Create products
        self.products = []
        for i in range(1, 4):  # 3 products
            ean = f"10000000000{i}"
            product = StoreHelper.get_or_create_product(
                ean=ean,
                name=f"Testproduct{i}",
                resell_price=Decimal("10.00") + i,
                discount=Decimal("0.00"),
                logger=self.logger,
            )[1]
            self.products.append(product)

    def _restock_product(self, product_index, quantity, purchase_price):
        """Helper function to restock a product."""
        response, restock = StoreHelper.restock_product(
            ean=self.products[product_index].ean,
            quantity=quantity,
            purchase_price=purchase_price,
            auth_user=self.admin,
            logger=self.logger,
            used_store_equity=False,
        )
        return restock

    def test_restock_and_purchase_until_zero(self):
        """Test restocking a product and purchasing until inventory is depleted."""
        product_index = 0
        product = self.products[product_index]

        # Restock the product
        self._restock_product(product_index, 5, Decimal("5.00"))

        # Purchase all items in stock
        for _ in range(5):
            response, purchase = StoreHelper.customer_purchase(
                ean=product.ean,
                quantity=1,
                card_number=self.customers[0].card_number,
                logger=self.logger,
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(purchase.product, product)

        # Verify inventory is zero
        self.assertEqual(ProductInventory.objects.filter(restock__product=product, remaining_quantity__gt=0).count(), 0)

    def test_partial_purchase_and_restock(self):
        """Test partial purchase followed by a restock."""
        product_index = 1
        product = self.products[product_index]

        # Initial restock
        self._restock_product(product_index, 10, Decimal("4.00"))

        # Purchase some items
        for _ in range(3):
            response, purchase = StoreHelper.customer_purchase(
                ean=product.ean,
                quantity=1,
                card_number=self.customers[1].card_number,
                logger=self.logger,
            )
            self.assertEqual(response.status_code, 200)

        # Verify remaining inventory
        inventory = ProductInventory.objects.filter(restock__product=product).aggregate(total_quantity=models.Sum('remaining_quantity'))
        self.assertEqual(inventory['total_quantity'], 7)

        # Restock again
        self._restock_product(product_index, 5, Decimal("6.00"))

        # Verify updated inventory
        inventory = ProductInventory.objects.filter(restock__product=product).aggregate(total_quantity=models.Sum('remaining_quantity'))
        self.assertEqual(inventory['total_quantity'], 12)

    def test_multiple_purchases_and_profit_calculation(self):
        """Test purchasing multiple products and calculating profits."""
        product_index = 2
        product = self.products[product_index]

        # Restock the product
        self._restock_product(product_index, 8, Decimal("7.00"))

        # Make multiple purchases
        for _ in range(4):
            response, purchase = StoreHelper.customer_purchase(
                ean=product.ean,
                quantity=1,
                card_number=self.customers[2].card_number,
                logger=self.logger,
            )
            self.assertEqual(response.status_code, 200)

            # Verify profit calculation
            self.assertEqual(purchase.expenses, Decimal("7.00"))
            self.assertEqual(purchase.revenue, product.resell_price)
            self.assertEqual(purchase.profit, product.resell_price - Decimal("7.00"))

    def test_purchase_exceeding_inventory(self):
        """Test purchasing more than available inventory raises an error."""
        product_index = 0
        self._restock_product(product_index, 5, Decimal("5.00"))

        with self.assertRaises(Exception):
            StoreHelper.customer_purchase(
                ean=self.products[product_index].ean,
                quantity=6,
                card_number=self.customers[0].card_number,
                logger=self.logger,
            )

    def test_restock_after_depletion_and_purchase_again(self):
        """Test restocking after inventory depletion and making more purchases."""
        product_index = 1
        product = self.products[product_index]

        # Initial restock
        self._restock_product(product_index, 3, Decimal("4.00"))

        # Purchase all items
        for _ in range(3):
            response, purchase = StoreHelper.customer_purchase(
                ean=product.ean,
                quantity=1,
                card_number=self.customers[1].card_number,
                logger=self.logger,
            )
            self.assertEqual(response.status_code, 200)

        # Verify inventory is zero
        self.assertEqual(ProductInventory.objects.filter(restock__product=product, remaining_quantity__gt=0).count(), 0)

        # Restock again
        self._restock_product(product_index, 5, Decimal("6.00"))

        # Make more purchases
        for _ in range(2):
            response, purchase = StoreHelper.customer_purchase(
                ean=product.ean,
                quantity=1,
                card_number=self.customers[2].card_number,
                logger=self.logger,
            )
            self.assertEqual(response.status_code, 200)

    def test_purchase_spanning_multiple_restocks(self):
        """Test a single purchase that spans multiple restocks."""
        product_index = 2
        product = self.products[product_index]

        # Restock with different prices
        self._restock_product(product_index, 3, Decimal("4.00"))
        self._restock_product(product_index, 3, Decimal("6.00"))

        # Purchase items spanning both restocks
        response, purchase = StoreHelper.customer_purchase(
            ean=product.ean,
            quantity=5,
            card_number=self.customers[0].card_number,
            logger=self.logger,
        )
        self.assertEqual(response.status_code, 200)

        # Verify profit calculation
        self.assertEqual(purchase.expenses, Decimal("24.00"))  # 3x4.00 + 2x6.00
        self.assertEqual(purchase.revenue, product.resell_price * 5)
        self.assertEqual(purchase.profit, (product.resell_price * 5) - Decimal("24.00"))
