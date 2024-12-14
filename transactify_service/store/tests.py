from django.test import TestCase

# Create your tests here.
from django.test import TestCase


from store.helpers.ManageStockHelper import StoreHelper
from decimal import Decimal
from django.contrib.auth.models import User

from .webmodels.Customer import Customer

from .webmodels.StoreProduct import StoreProduct
from .webmodels.CustomerPurchase import CustomerPurchase
from .webmodels.CustomerDeposit import CustomerDeposit
from .webmodels.CustomerBalance import CustomerBalance
from .webmodels.ProductRestock import ProductRestock
from django.contrib.auth.models import User, Group


class StoreHelperTestCase(TestCase):

    def setUp(self):
        pass

    def test_create_customer(self):
        """
        Test creating a new customer.
        """
        StoreHelper.create_new_customer(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@test.com",
            balance=Decimal("50.00"),
            card_number="123456789")
        
        customer = Customer.objects.get(card_number="123456789")
        self.assertEqual(customer.user.first_name, "Test")
        self.assertEqual(customer.user.last_name, "User")
        self.assertEqual(customer.user.email, "test@test.com")
        #self.assertEqual(customer.balance, Decimal("50.00"))



    def test_customer_purchase_success(self):
        """
        Test successful customer purchase.
        """
        response, _ = StoreHelper.customer_purchase(
            ean=self.product.ean,
            quantity=2,
            card_number=self.customer.card_number
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.product.stock_quantity, 8)  # 2 items purchased
        updated_balance = CustomerBalance.objects.get(customer=self.customer).balance
        self.assertEqual(updated_balance, Decimal("30.00"))  # 50 - (2 * 10)

    def test_customer_purchase_insufficient_balance(self):
        """
        Test purchase failure due to insufficient balance.
        """
        self.customer_balance.balance = Decimal("10.00")
        self.customer_balance.save()

        response, _ = StoreHelper.customer_purchase(
            ean=self.product.ean,
            quantity=2,
            card_number=self.customer.card_number
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("Insufficient balance", response.data["error"])

    def test_customer_purchase_insufficient_stock(self):
        """
        Test purchase failure due to insufficient stock.
        """
        self.product.stock_quantity = 1
        self.product.save()

        response, _ = StoreHelper.customer_purchase(
            ean=self.product.ean,
            quantity=2,
            card_number=self.customer.card_number
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("Insufficient stock", response.data["warning"])

    def test_customer_add_deposit(self):
        """
        Test adding a deposit to the customer's account.
        """
        response, deposit_entry = StoreHelper.customer_add_deposit(
            customer=self.customer,
            amount=Decimal("20.00")
        )
        self.assertEqual(response.status_code, 200)
        updated_balance = CustomerBalance.objects.get(customer=self.customer).balance
        self.assertEqual(updated_balance, Decimal("70.00"))  # 50 + 20
        self.assertIsNotNone(deposit_entry)

    def test_restock_product(self):
        """
        Test restocking a product.
        """
        response, product = StoreHelper.restock_product(
            ean=self.product.ean,
            quantity=5,
            purchase_price=Decimal("8.00")
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(product.stock_quantity, 15)  # 10 + 5

    def test_create_new_customer(self):
        """
        Test creating a new customer and their initial deposit.
        """
        response, customer = StoreHelper.create_new_customer(
            username="newuser",
            first_name="New",
            last_name="User",
            email="newuser@example.com",
            balance=Decimal("20.00"),
            card_number="987654321"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(customer.card_number, "987654321")
        customer_balance = CustomerBalance.objects.get(customer=customer)
        self.assertEqual(customer_balance.balance, Decimal("20.00"))

    def test_get_stock_quantity(self):
        """
        Test calculation of stock quantity.
        """
        # Simulate a restock and a purchase
        ProductRestock.objects.create(
            product=self.product,
            quantity=5,
            purchase_price=Decimal("8.00"),
            total_cost=Decimal("40.00")
        )
        CustomerPurchase.objects.create(
            product=self.product,
            quantity=3,
            purchase_price=Decimal("10.00"),
            customer=self.customer,
            customer_balance=self.customer_balance.balance
        )

        stock_quantity = StoreHelper._get_stock_quantity(self.product)
        self.assertEqual(stock_quantity, 12)  # 10 (initial) + 5 (restock) - 3 (purchase)
