

from store.helpers.ManageStockHelper import StoreHelper
import logging

from django.contrib.auth.models import User
from store.webmodels.Customer import Customer
from store.webmodels.StoreProduct import StoreProduct
from store.webmodels.ProductRestock import ProductRestock
from store.webmodels.CustomerDeposit import CustomerDeposit
from store.webmodels.CustomerPurchase import CustomerPurchase

import random
from datetime import datetime, timedelta

class Product():
    def __init__(self, name, ean, weight, resell_price):
        self.name = name
        self.ean = ean
        self.weight = weight
        self.resell_price = resell_price
      

class HistoricalData():
    CONST_Alesto_Cruspies_überzogene_Erdnüsse_Paprika="2005702"
    CONST_Alesto_Erdnüsse_pikant_gewürzt="2005672"
    CONST_Alesto_Studentenfutter_Classic="2005726"
    CONST_Alesto_Nussmix_mit_Makadamia="20772970"
    CONST_Alesto_Nuts_Royal="250047238"
    CONST_Alesto_Nussmix_mit_Pistazie="20559625"
    CONST_Alesto_Nuss_Frucht_Mix="20815394"
    CONST_Alesto_Cashew_Cranberry_Mix="20815400"
    CONST_Alesto_Cashew_Erdnuss_Mix__Honig_Salz_="20333737"
    CONST_SnackFun_Teigumantelte_Erdnüsse="409920000442"
    CONST_SnackFun_Teigumantelte_Erdnüsse__Wasabi_="409920000466"
    CONST_SnackFun_Pistazien__gesalzen_="4099200046686"
    CONST_SnackFun_Pistazien__ungesalzen_="4099200046687"
    CONST_SnackFun_Macadamia="4099200046754"
    CONST_SnackFun_Erdnüsse="4099200046730"
    CONST_Bio_Natura_Cashew_Cranberry="4104420026681"
    CONST_Bio_Natura_Studentenfutter="4061462405839"
    CONST_Asia_Snack_Shogun_Mix="4047247108225"
    CONST_ZZM_Apfelchips="4099200143286"

    def __init__(self):
        debug_offset_date = timedelta(days=0)
        self.logger = logging.getLogger('HistData')    
        self.username = "anonymous"
        self.first_name = "Anon"
        self.last_name = "Ymous"
        self.email = "anon.ymous@store.com"
        self.card_number = "NoCardNumber"

        # Add the products
        products = [
            Product('Alesto Cruspies überzogene Erdnüsse Paprika', self.CONST_Alesto_Cruspies_überzogene_Erdnüsse_Paprika, 200, 1.5),
            Product('Alesto Erdnüsse pikant gewürzt', self.CONST_Alesto_Erdnüsse_pikant_gewürzt, 150, 1.5),
            Product('Alesto Studentenfutter Classic', self.CONST_Alesto_Studentenfutter_Classic, 200, 2.5),
            Product('Alesto Nussmix mit Makadamia', self.CONST_Alesto_Nussmix_mit_Makadamia, 200, 3.2),
            Product('Alesto Nuts Royal', self.CONST_Alesto_Nuts_Royal, 200, 3.2),
            Product('Alesto Nussmix mit Pistazie', self.CONST_Alesto_Nussmix_mit_Pistazie, 200, 3.2),
            Product('Alesto Nuss-Frucht-Mix', self.CONST_Alesto_Nuss_Frucht_Mix, 200, 2.5),
            Product('Alesto Cashew-Cranberry-Mix', self.CONST_Alesto_Cashew_Cranberry_Mix, 200, 2.5),
            Product('Alesto Cashew-Erdnuss-Mix (Honig Salz)', self.CONST_Alesto_Cashew_Erdnuss_Mix__Honig_Salz_, 200, 2.5),
            Product('SnackFun Teigumantelte Erdnüsse', self.CONST_SnackFun_Teigumantelte_Erdnüsse, 200, 1.5),
            Product('SnackFun Teigumantelte Erdnüsse (Wasabi)', self.CONST_SnackFun_Teigumantelte_Erdnüsse__Wasabi_, 200, 1.5),
            Product('SnackFun Pistazien (gesalzen)', self.CONST_SnackFun_Pistazien__gesalzen_, 250, 4.5),
            Product('SnackFun Pistazien (ungesalzen)', self.CONST_SnackFun_Pistazien__ungesalzen_, 250, 4.5),
            Product('SnackFun Macadamia', self.CONST_SnackFun_Macadamia, 125, 3.5),
            Product('SnackFun Erdnüsse', self.CONST_SnackFun_Erdnüsse, 500, 3.2),
            Product('Bio Natura Cashew-Cranberry', self.CONST_Bio_Natura_Cashew_Cranberry, 300, 4.5),
            Product('Bio Natura Studentenfutter', self.CONST_Bio_Natura_Studentenfutter, 300, 4.5),
            Product('Asia-Snack Shogun Mix', self.CONST_Asia_Snack_Shogun_Mix, 150, 2.0),
            Product('ZZM Apfelchips', self.CONST_ZZM_Apfelchips, 100, 3.7)
        ]
        self.date = datetime.strptime('27.04.2024', '%d.%m.%Y') + debug_offset_date
        # Create the user
        self.add_anonymous_customer()

        # Register the products
        for product in products:
            self.add_product(product.ean, product.name, product.resell_price)

        # Alesto Cruspies überzogene Erdnüsse Paprika	2005702	2	 € 0,99 
        # Alesto Erdnüsse pikant gewürzt	2005672	2	 € 0,89 
        # Alesto Studentenfutter Classic	20333737	2	 € 1,99 
        # Alesto Nussmix mit Makadamia	2005672	2	 € 2,59 
        # Alesto Nuts Royal	250047238	2	 € 2,65 
        self.date = datetime.strptime('28.04.2024', '%d.%m.%Y') + debug_offset_date
        self.date_end = datetime.strptime('01.10.2024', '%d.%m.%Y') + debug_offset_date
        self.add_stock(self.CONST_Alesto_Cruspies_überzogene_Erdnüsse_Paprika, 2, 0.99)
        self.add_stock(self.CONST_Alesto_Erdnüsse_pikant_gewürzt, 2, 0.89)
        self.add_stock(self.CONST_Alesto_Cashew_Erdnuss_Mix__Honig_Salz_, 2, 1.99)
        self.add_stock(self.CONST_Alesto_Erdnüsse_pikant_gewürzt, 2, 2.59)
        self.add_stock(self.CONST_Alesto_Nuts_Royal, 2, 2.65)

        # Alesto Studentenfutter Classic	20333737	1	 € 1,99 
        # Alesto Nussmix mit Makadamia	2005672	2	 € 2,59 
        # Alesto Nuts Royal	250047238	4	 € 2,65 
        # Alesto Nussmix mit Pistazie	2005672	2	 € 2,59 
        # Alesto Nuss-Frucht-Mix	2005672	2	 € 1,99 
        # Alesto Cashew-Erdnuss-Mix (Honig Salz)	#NV	2	 € 1,99 
        # SnackFun Teigumantelte Erdnüsse	409920000442	4	 € 0,99 
        # SnackFun Pistazien (gesalzen)	20333737	3	 € 3,74 
        # SnackFun Pistazien (ungesalzen)	20333737	1	 € 3,74 
        # SnackFun Macadamia	20333737	3	 € 2,79 
        # SnackFun Erdnüsse	20333737	2	 € 2,69 
        self.date = self.date_end
        self.date_end = datetime.strptime('11.10.2024', '%d.%m.%Y') + debug_offset_date
        self.add_stock(self.CONST_Alesto_Studentenfutter_Classic, 1, 1.99)
        self.add_stock(self.CONST_Alesto_Nussmix_mit_Makadamia, 2, 2.59)
        self.add_stock(self.CONST_Alesto_Nuts_Royal, 4, 2.65)
        self.add_stock(self.CONST_Alesto_Nussmix_mit_Pistazie, 2, 2.59)
        self.add_stock(self.CONST_Alesto_Nuss_Frucht_Mix, 2, 1.99)
        self.add_stock(self.CONST_Alesto_Cashew_Erdnuss_Mix__Honig_Salz_, 2, 1.99)
        self.add_stock(self.CONST_SnackFun_Teigumantelte_Erdnüsse, 4, 0.99)
        self.add_stock(self.CONST_SnackFun_Pistazien__gesalzen_, 3, 3.74)
        self.add_stock(self.CONST_SnackFun_Pistazien__ungesalzen_, 1, 3.74)
        self.add_stock(self.CONST_SnackFun_Macadamia, 3, 2.79)
        self.add_stock(self.CONST_SnackFun_Erdnüsse, 2, 2.69)

        # Alesto Studentenfutter Classic	20333737	4	 € 1,99 
        # Alesto Nuts Royal	250047238	2	 € 2,65 
        # Alesto Nussmix mit Pistazie	2005672	2	 € 2,59 
        # Alesto Nuss-Frucht-Mix	2005672	2	 € 1,99 
        # Alesto Cashew-Cranberry-Mix	#NV	2	 € 1,99 
        # Alesto Cashew-Erdnuss-Mix (Honig Salz)	#NV	4	 € 1,99 
        # SnackFun Teigumantelte Erdnüsse (Wasabi)	4047247108225	2	 € 0,99 
        # Bio Natura Cashew-Cranberry	20333737	2	 € 3,48 
        # Bio Natura Studentenfutter	20333737	2	 € 3,48 
        # Asia-Snack Shogun Mix	20333737	1	 € 1,49 
        # ZZM Apfelchips	4099200143286	1	 € 2,99 
        self.date = self.date_end
        self.date_end = datetime.strptime('06.11.2024', '%d.%m.%Y') + debug_offset_date
        self.add_stock(self.CONST_Alesto_Studentenfutter_Classic, 4, 1.99)
        self.add_stock(self.CONST_Alesto_Nuts_Royal, 2, 2.65)
        self.add_stock(self.CONST_Alesto_Nussmix_mit_Pistazie, 2, 2.59)
        self.add_stock(self.CONST_Alesto_Nuss_Frucht_Mix, 2, 1.99)
        self.add_stock(self.CONST_Alesto_Cashew_Cranberry_Mix, 2, 1.99)
        self.add_stock(self.CONST_Alesto_Cashew_Erdnuss_Mix__Honig_Salz_, 4, 1.99)
        self.add_stock(self.CONST_SnackFun_Teigumantelte_Erdnüsse__Wasabi_, 2, 0.99)
        self.add_stock(self.CONST_Bio_Natura_Cashew_Cranberry, 2, 3.48)
        self.add_stock(self.CONST_Bio_Natura_Studentenfutter, 2, 3.48)
        self.add_stock(self.CONST_Asia_Snack_Shogun_Mix, 1, 1.49)
        self.add_stock(self.CONST_ZZM_Apfelchips, 1, 2.99)

        # Alesto Erdnüsse pikant gewürzt	2005672	4	 € 0,89 
        # Alesto Studentenfutter Classic	20333737	3	 € 1,99 
        # Alesto Nussmix mit Makadamia	2005672	2	 € 2,59 
        # Alesto Nuts Royal	250047238	3	 € 2,65 
        # Alesto Nussmix mit Pistazie	2005672	2	 € 2,59 
        # Alesto Nuss-Frucht-Mix	2005672	3	 € 1,99 
        # Alesto Cashew-Cranberry-Mix	#NV	4	 € 1,99 
        # Alesto Cashew-Erdnuss-Mix (Honig Salz)	#NV	4	 € 1,99 
        # SnackFun Teigumantelte Erdnüsse	409920000442	4	 € 0,99 
        # SnackFun Teigumantelte Erdnüsse (Wasabi)	4047247108225	1	 € 0,99 
        self.date = self.date_end
        self.date_end = datetime.strptime('11.11.2024', '%d.%m.%Y') + debug_offset_date
        self.add_stock(self.CONST_Alesto_Erdnüsse_pikant_gewürzt, 4, 0.89)
        self.add_stock(self.CONST_Alesto_Studentenfutter_Classic, 3, 1.99)
        self.add_stock(self.CONST_Alesto_Nussmix_mit_Makadamia, 2, 2.59)
        self.add_stock(self.CONST_Alesto_Nuts_Royal, 3, 2.65)
        self.add_stock(self.CONST_Alesto_Nussmix_mit_Pistazie, 2, 2.59)
        self.add_stock(self.CONST_Alesto_Nuss_Frucht_Mix, 3, 1.99)
        self.add_stock(self.CONST_Alesto_Cashew_Cranberry_Mix, 4, 1.99)
        self.add_stock(self.CONST_Alesto_Cashew_Erdnuss_Mix__Honig_Salz_, 4, 1.99)
        self.add_stock(self.CONST_SnackFun_Teigumantelte_Erdnüsse, 4, 0.99)
        self.add_stock(self.CONST_SnackFun_Teigumantelte_Erdnüsse__Wasabi_, 1, 0.99)


 



    def add_anonymous_customer(self, init_balance = 1):
        """Add an anonymous customer to the database."""
        try:
            logger_mock_store_customers = logging.getLogger('CreateNewCustomer')
            rsp, customer = StoreHelper.create_new_customer(username=self.username, 
                                        first_name=self.first_name, last_name=self.last_name, 
                                        email=self.email, 
                                        balance=init_balance, 
                                        card_number=self.card_number , 
                                        logger=self.logger)
            customer.issued_at = self.date
        except Exception as e:
            self.logger.error(f"Failed to add anonymous customer: {e}")

    def add_deposits(self, username, amount):
        try:
            user = User.objects.get(username=username)
        except Exception as e:
            self.logger.error(f"Failed to get user {username}: {e}")
        
        try:
            customer = Customer.objects.get(user=user)
        except Exception as e:
            self.logger.error(f"Failed to get customer user{i}: {e}")

        
        rsp, customer_deposit = StoreHelper.customer_add_deposit(customer, amount, self.logger)
        
    
    def purchase_all(self, ean):
        number_of_products = StoreProduct.objects.get(ean=ean).stock_quantity
        for i in range(0, number_of_products):
            self.add_purchase(ean)

    def add_purchase(self, product_ean):
        try:
            user = User.objects.get(username=self.username)
        except Exception as e:
            self.logger.error(f"Failed to get user {self.username}: {e}")
        
        try:
            customer = Customer.objects.get(user=user)
        except Exception as e:
            self.logger.error(f"Failed to get customer for user {self.username}: {e}")
            
        try:
            product = StoreProduct.objects.get(ean=product_ean)
        except Exception as e:
            self.logger.error(f"Failed to get product test_product{i}: {e}")
        
        # bevore each purchase, deposit the exact amount
        rsp, customer_deposit = StoreHelper.customer_add_deposit(customer, product.resell_price, self.logger)
        
       # def customer_purchase(ean: str, quantity: int, card_number: str, logger: logging.Logger) -> tuple[Response, Customer]:
        rsp, customer_purchase = StoreHelper.customer_purchase(
            product.ean, 1, customer.card_number, 
            self.logger)
        
        # generate a date beween self.date and self.date_end -1
        gendate = self.date + timedelta(days=random.randint(0, (self.date_end - self.date).days - 1))
        customer_purchase.purchase_date = gendate
        customer_deposit.deposit_date = gendate - timedelta(days=random.randint(0, 7))
        customer_deposit.save()
        customer_purchase.save()
        

    def add_product(self, ean, name, resell_price):
        try:
            rsp, product = StoreHelper.get_or_create_product(
                ean=ean, 
                name=name, 
                resell_price=resell_price, 
                discount=0,
                logger=self.logger)
            product.added_at = self.date
            product.save()
        except Exception as e:
            self.logger.error(f"Failed to add product: {e}")

    def add_stock(self, ean, quantity, purchase_price, used_store_equity=False):
        try:
            product = StoreProduct.objects.get(ean=ean)
        except Exception as e:
            self.logger.error(f"Failed to get product {ean}: {e}")
            
        try:
            rsp, product_restock = StoreHelper.restock_product(ean, quantity, 
                                                               purchase_price,
                                                               self.logger,
                                                               auth_user=User.objects.get(username=self.username),
                                                               used_store_equity=used_store_equity)
            product_restock.restock_date = self.date
            product_restock.save()
        except Exception as e:
            self.logger.error(f"Failed to restock product {ean}: {e}")

        # immediately purchase the products
        self.purchase_all(ean)