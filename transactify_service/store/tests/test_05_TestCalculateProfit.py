from decimal import Decimal
from django.test import TestCase
from store.webmodels.Customer import Customer
from store.webmodels.StoreProduct import StoreProduct
from store.webmodels.ProductRestock import ProductRestock
from store.webmodels.CustomerPurchase import CustomerPurchase
from store.webmodels.ProductInventory import ProductInventory
from django.contrib.auth.models import User
import logging

from decimal import Decimal
from django.contrib.auth.models import User
from store.webmodels.StoreProduct import StoreProduct
from store.webmodels.ProductRestock import ProductRestock
from store.helpers.ManageStockHelper import StoreHelper
from django.test import TestCase
import logging
from decimal import Decimal
from unittest import skip

class TestSetupForMultipleUsersAndProducts(TestCase):
    PRODUCT_ONE = 0
    PRODUCT_TWO = 1
    PRODUCT_THREE = 2

    def setUp(self):
        self.admin = User.objects.get_or_create(username="admin")[0]

        """Set up multiple users, products, and restocks."""
        self.logger = logging.getLogger("TestSetupForMultipleUsersAndProducts")
        self.logger.setLevel(logging.INFO)

        # Create multiple users
        self.customers: list[Customer] = []
        for i in range(1, 6):  # 5 users
            _, cust = StoreHelper.create_new_customer(
                username=f"testuser{i}",
                first_name=f"Test{i}",
                last_name=f"User",
                email=f"test@test.com",
                balance=Decimal("100.00"),
                card_number=f"123456789012345{i}",
                logger=self.logger
            )
            self.customers.append(cust)
        # Create multiple products
        self.products: list[StoreProduct] = []
        self.products_prices: list[Decimal] = []
        for i in range(1, 6):  # 5 products
            ean = f"10000000000{i}"
            product = StoreHelper.get_or_create_product(
                ean=ean,
                name=f"Testproduct{i}",
                resell_price=Decimal("10.99") + i,
                discount=Decimal("0.00"),
                logger=self.logger,
            )[1]
            self.products.append(product)
            self.products_prices.append(product.resell_price)
    
    def _restock_product(self, quantity: int, purchase_price: Decimal, product_index: int):
        purchase_prices = []
        _, rs = StoreHelper.restock_product(
            ean=self.products[product_index].ean,
            quantity=quantity,
            purchase_price=Decimal(purchase_price),  # Vary purchase price for each restock
            auth_user=self.admin,  # Use the first user for restocks
            logger=self.logger,
            used_store_equity=False,
        )
        for i in range(0, quantity): 
            purchase_prices.append( 
                rs.purchase_price.quantize(Decimal("0.01")))
        return purchase_prices, rs
    
    def _create_restock_1(self):
        purchase_prices = []
        ppl, rs1 = self._restock_product(3, 3.99, self.PRODUCT_ONE)
        purchase_prices.extend(ppl)

        # Restock product 2
        ppl, rs2 = self._restock_product(5, 5.79, self.PRODUCT_TWO)
        purchase_prices.extend(ppl)

        # Restock product 3
        ppl, rs3 = self._restock_product(2, 7.99, self.PRODUCT_THREE)
        purchase_prices.extend(ppl)

        restocks = [rs1, rs2, rs3]
        return restocks, purchase_prices
    

    def _create_restock_2(self):
        purchase_prices = []


        ppl, rs1 = self._restock_product(1, 3.99, self.PRODUCT_ONE)
        purchase_prices.extend(ppl)


        ppl, rs2 = self._restock_product(5, 5.79, self.PRODUCT_ONE)
        purchase_prices.extend(ppl)
        
        # Restock product 2
        _, rs_ = self._restock_product(5, 6.29, self.PRODUCT_TWO)

        ppl, rs3 = self._restock_product(2, 7.99, self.PRODUCT_ONE)
        purchase_prices.extend(ppl)

        # Restock product 3
        _, rs_ = self._restock_product(5, 4.39, self.PRODUCT_THREE)

        restocks = [rs1, rs2, rs3]
        print(purchase_prices)
        return restocks, purchase_prices

    def test_single_purchase_within_one_restock(self):
        """Test profit calculation for a purchase that uses inventory from a single restock."""
        self.logger.info("\n*****Testing single purchase within one restock*****\n")
        pn = 0
        restocks, purchase_prices = self._create_restock_1()
    
        # ean: str, quantity: int, card_number: str, logger: logging.Logger, *args, **kwargs) -> tuple[Response, CustomerPurchase]:
        _, purchase = StoreHelper.customer_purchase(
            ean=self.products[pn].ean,
            quantity=1,
            card_number=self.customers[0].card_number,
            logger=self.logger,
        )
        purchase_price = purchase_prices[pn]
        self.assertEqual(purchase.expenses, purchase_price)  
        self.assertEqual(purchase.revenue, self.products[pn].resell_price)  
        self.assertEqual(purchase.profit, self.products[pn].resell_price - purchase_price)  
    
    def test_two_purchases_with_different_costs(self):
        """Test profit calculation for a purchase that uses inventory from a single restock."""
        self.logger.info("\n*****Testing single purchase within one restock*****\n")
        
        product_selection = 0
        restocks, purchase_prices = self._create_restock_1()
        # ean: str, quantity: int, card_number: str, logger: logging.Logger, *args, **kwargs) -> tuple[Response, CustomerPurchase]:
        _, purchase = StoreHelper.customer_purchase(
            ean=self.products[product_selection].ean,
            quantity=2,
            card_number=self.customers[0].card_number,
            logger=self.logger,
        )
        purchase_price = purchase_prices[product_selection]
        self.assertEqual(purchase.expenses, purchase_price*purchase.quantity)  
        self.assertEqual(purchase.revenue, self.products[product_selection].resell_price*purchase.quantity)  
        self.assertEqual(purchase.profit, (self.products[product_selection].resell_price - purchase_price)*purchase.quantity)  
        
        _, purchase = StoreHelper.customer_purchase(
            ean=self.products[product_selection].ean,
            quantity=1,
            card_number=self.customers[0].card_number,
            logger=self.logger,
        )
        purchase_price = purchase_prices[product_selection+1]
        self.assertEqual(purchase.expenses, purchase_price)  
        self.assertEqual(purchase.revenue, self.products[product_selection].resell_price)  
        self.assertEqual(purchase.profit, self.products[product_selection].resell_price - purchase_price)  

    def test_three_purchases_with_different_costs(self):
        """Test profit calculation for a purchase that uses inventory from a single restock."""
        self.logger.info("\n-------------------------------------------------------------------------------\n")
        self.logger.info("\n*****Testing three purchases with different costs*****\n")
        
        product_selection = 0
        restocks, purchase_prices = self._create_restock_2()
        # ean: str, quantity: int, card_number: str, logger: logging.Logger, *args, **kwargs) -> tuple[Response, CustomerPurchase]:
        for i in range(0, 3):
            _, purchase = StoreHelper.customer_purchase(
                ean=self.products[product_selection].ean,
                quantity=1,
                card_number=self.customers[0].card_number,
                logger=self.logger,
            )
            purchase_price = purchase_prices[i]
            self.assertEqual(purchase.expenses, purchase_price)  
            self.assertEqual(purchase.revenue, self.products[product_selection].resell_price)  
            self.assertEqual(purchase.profit, self.products[product_selection].resell_price - purchase_price)

        self.logger.info("\n-------------------------------------------------------------------------------\n")
 
    def test_four_purchases_with_different_costs_single_purchase(self):
        """Test profit calculation for a purchase that uses inventory from a single restock."""
        self.logger.info("\n-------------------------------------------------------------------------------\n")
        self.logger.info("\n***** Testing three purchases with different costs *****\n")
        
        product_selection = 0
        restocks, purchase_prices = self._create_restock_2()
        # ean: str, quantity: int, card_number: str, logger: logging.Logger, *args, **kwargs) -> tuple[Response, CustomerPurchase]:

        _, purchase = StoreHelper.customer_purchase(
            ean=self.products[product_selection].ean,
            quantity=2,
            card_number=self.customers[0].card_number,
            logger=self.logger,
        )
        purchase_price = purchase_prices[1]
        self.assertEqual(purchase.expenses, purchase_price)  
        self.assertEqual(purchase.revenue, self.products[product_selection].resell_price)  
        self.assertEqual(purchase.profit, self.products[product_selection].resell_price - purchase_price)

        _, purchase = StoreHelper.customer_purchase(
                        ean=self.products[product_selection].ean,
                        quantity=2,
                        card_number=self.customers[0].card_number,
                        logger=self.logger,
        )
        purchase_price = purchase_prices[3]
        self.assertEqual(purchase.expenses, purchase_price)  
        self.assertEqual(purchase.revenue, self.products[product_selection].resell_price)  
        self.assertEqual(purchase.profit, self.products[product_selection].resell_price - purchase_price)


        self.logger.info("\n-------------------------------------------------------------------------------\n")
 
 


    # def test_purchase_spanning_multiple_restocks(self):
    #     """Test profit calculation for a purchase that spans multiple restocks."""
    #     purchase = CustomerPurchase.objects.create(
    #         product=self.product,
    #         quantity=20,
    #         purchase_price=Decimal("15.00"),
    #         customer=self.customer,
    #         customer_balance=self.customer.balance - Decimal("300.00"),
    #     )
    #     purchase.calculate_profit(self.logger)

    #     # Expenses: 10 from restock1 (10 x 5.00) + 10 from restock2 (10 x 6.00)
    #     self.assertEqual(purchase.expenses, Decimal("110.00"))
    #     self.assertEqual(purchase.revenue, Decimal("300.00"))  # 20 x 15.00
    #     self.assertEqual(purchase.profit, Decimal("190.00"))  # Revenue - Expenses

    # def test_purchase_exceeding_inventory(self):
    #     """Test profit calculation for a purchase exceeding available inventory."""
    #     with self.assertRaises(Exception) as context:
    #         purchase = CustomerPurchase.objects.create(
    #             product=self.product,
    #             quantity=50,
    #             purchase_price=Decimal("15.00"),
    #             customer=self.customer,
    #             customer_balance=self.customer.balance - Decimal("750.00"),
    #         )
    #         purchase.calculate_profit(self.logger)

    #     self.assertTrue("Insufficient inventory" in str(context.exception))

    # def test_purchase_exact_inventory(self):
    #     """Test profit calculation for a purchase that uses the exact total inventory."""
    #     total_quantity = (
    #         self.restock1.quantity
    #         + self.restock2.quantity
    #         + self.restock3.quantity
    #     )
    #     purchase = CustomerPurchase.objects.create(
    #         product=self.product,
    #         quantity=total_quantity,
    #         purchase_price=Decimal("15.00"),
    #         customer=self.customer,
    #         customer_balance=self.customer.balance - Decimal("750.00"),
    #     )
    #     purchase.calculate_profit(self.logger)

    #     # Expenses: 10 x 5.00 + 15 x 6.00 + 20 x 7.00 = 290.00
    #     self.assertEqual(purchase.expenses, Decimal("290.00"))
    #     self.assertEqual(purchase.revenue, Decimal("675.00"))  # 45 x 15.00
    #     self.assertEqual(purchase.profit, Decimal("385.00"))  # Revenue - Expenses

    # def test_partial_inventory_update(self):
    #     """Test that inventory is properly updated after a purchase."""
    #     purchase = CustomerPurchase.objects.create(
    #         product=self.product,
    #         quantity=15,
    #         purchase_price=Decimal("15.00"),
    #         customer=self.customer,
    #         customer_balance=self.customer.balance - Decimal("225.00"),
    #     )
    #     purchase.calculate_profit(self.logger)

    #     # Expenses: 10 x 5.00 (from restock1) + 5 x 6.00 (from restock2) = 65.00
    #     self.assertEqual(purchase.expenses, Decimal("65.00"))
    #     self.assertEqual(purchase.revenue, Decimal("225.00"))  # 15 x 15.00
    #     self.assertEqual(purchase.profit, Decimal("160.00"))  # Revenue - Expenses

    #     # Verify inventory updates
    #     inventory1 = ProductInventory.objects.get(restock=self.restock1)
    #     inventory2 = ProductInventory.objects.get(restock=self.restock2)

    #     self.assertEqual(inventory1.remaining_quantity, 0)  # All 10 used
    #     self.assertEqual(inventory2.remaining_quantity, 10)  # 15 - 5 used

    # def test_no_inventory_left(self):
    #     """Test that no inventory is left after exact total quantity is purchased."""
    #     total_quantity = (
    #         self.restocks[1].quantity
    #         + self.restocks[2].quantity
    #         + self.restocks[3].quantity
    #     )
    #     purchase = CustomerPurchase.objects.create(
    #         product=self.product,
    #         quantity=total_quantity,
    #         purchase_price=Decimal("15.00"),
    #         customer=self.customer,
    #         customer_balance=self.customer.balance - Decimal("675.00"),
    #     )
    #     purchase.calculate_profit(self.logger)

    #     # Verify inventory updates
    #     inventory1 = ProductInventory.objects.get(restock=self.restock1)
    #     inventory2 = ProductInventory.objects.get(restock=self.restock2)
    #     inventory3 = ProductInventory.objects.get(restock=self.restock3)

    #     self.assertEqual(inventory1.remaining_quantity, 0)  # All 10 used
    #     self.assertEqual(inventory2.remaining_quantity, 0)  # All 15 used
    #     self.assertEqual(inventory3.remaining_quantity, 0)  # All 20 used
