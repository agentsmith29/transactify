from django.db import models
from datetime import timedelta


class Product(models.Model):
    """ Model to store product names and their EAN codes """
    ean = models.CharField(max_length=13, primary_key=True)
    name = models.CharField(max_length=100)

    # Track the quantity of the product in stock
    stock_quantity = models.PositiveIntegerField(default=0)

    # Resell price is a fixed value for all products
    resell_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} (EAN: {self.ean})"


class StockProductPurchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()  # Quantity of the product purchased
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price per unit at the time of purchase
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)  # Total cost (quantity * purchase_price)
    purchase_date = models.DateTimeField(auto_now_add=True)  # Timestamp of the purchase

    def __str__(self):
        return f"{self.quantity} units of {self.product.name} purchased on {self.purchase_date}"


class StockProductSale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()  # Quantity of the product sold
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price per unit at the time of sale

    sale_date = models.DateTimeField(auto_now_add=True)  # Timestamp of the sale

    sold_to = models.ForeignKey('Customer', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quantity} units of {self.product.name} sold on {self.sale_date}"


class Customer(models.Model):
    card_number = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    issued_at = models.DateTimeField(auto_now_add=True)

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    #card_content = models.CharField(default="")

    def __str__(self):
        return f"{self.name}"


class CustomerDeposit(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Deposit of {self.amount} to {self.customer.name} on {self.timestamp}"


class CustomerWithdrawal(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Withdrawal of {self.amount} from {self.customer.name} on {self.timestamp}"


class CustomerPurchase(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    product = models.CharField(max_length=100)  # Product name or description
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Purchase of {self.product} by {self.customer.name} for {self.amount} on {self.timestamp}"

#class Stock(models.Model):
#    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE)
#    quantity = models.PositiveIntegerField(default=0)
#    #addition_date = models.DateTimeField(auto_now_add=True)#
#
#    def __str__(self):
#        return f"Added {self.quantity} units to {self.product.product_info.name}"

#class Sale(models.Model):
#    ean = models.ForeignKey(Product, on_delete=models.CASCADE)
#    quantity = models.PositiveIntegerField()
#    sale_date = models.DateTimeField(auto_now_add=True)
#    revenue = models.DecimalField(max_digits=10, decimal_places=2)
#    expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#
#    def calculate_earnings(self):
#        return self.revenue - self.expense
#
#    def __str__(self):
#        return f"Sale of {self.quantity} {self.ean.ean.name} on {self.sale_date}"
#
