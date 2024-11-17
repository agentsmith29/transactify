import sqlite3
from datetime import datetime

class SnackStore:
    def __init__(self, db_name='snack_store.db'):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Create tables with updated schema
        cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            ean TEXT NOT NULL UNIQUE,
                            price REAL NOT NULL,
                            stock INTEGER NOT NULL,
                            FOREIGN KEY (ean) REFERENCES product_names(ean))''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS product_names (
                            ean TEXT PRIMARY KEY,
                            name TEXT NOT NULL)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS sales (
                            id INTEGER PRIMARY KEY,
                            ean TEXT,
                            quantity INTEGER,
                            sale_date TEXT,
                            revenue REAL,
                            expense REAL,
                            FOREIGN KEY (ean) REFERENCES products(ean))''')
        
        conn.commit()
        conn.close()

    def add_product(self, ean, name, price, stock):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Insert into product_names table if EAN is new
        cursor.execute('INSERT OR IGNORE INTO product_names (ean, name) VALUES (?, ?)', (ean, name))
        
        # Insert into products table
        cursor.execute('INSERT OR REPLACE INTO products (ean, price, stock) VALUES (?, ?, ?)', (ean, price, stock))
        
        conn.commit()
        conn.close()

    def make_sale(self, ean, quantity):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT price, stock FROM products WHERE ean = ?', (ean,))
        product = cursor.fetchone()
        
        if product and product[1] >= quantity:  # Check if enough stock is available
            price, stock = product
            revenue = price * quantity
            expense = 0  # Assume no additional expenses for simplicity

            cursor.execute('INSERT INTO sales (ean, quantity, sale_date, revenue, expense) VALUES (?, ?, ?, ?, ?)',
                           (ean, quantity, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), revenue, expense))
            
            # Update stock
            cursor.execute('UPDATE products SET stock = stock - ? WHERE ean = ?', (quantity, ean))
            conn.commit()
            print(f'Sold {quantity} unit(s) of product with EAN {ean}. Revenue: {revenue}')
        else:
            print("Not enough stock available.")
        
        conn.close()

    def view_stock(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT p.id, n.ean, n.name, p.price, p.stock 
                          FROM products p 
                          JOIN product_names n ON p.ean = n.ean''')
        products = cursor.fetchall()
        print("Current Stock:")
        for prod in products:
            print(f"ID: {prod[0]}, EAN: {prod[1]}, Name: {prod[2]}, Price: {prod[3]}, Stock: {prod[4]}")
        conn.close()

    def view_sales_summary(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sales')
        sales = cursor.fetchall()
        print("Sales Summary:")
        for sale in sales:
            print(f"ID: {sale[0]}, EAN: {sale[1]}, Quantity: {sale[2]}, Date: {sale[3]}, Revenue: {sale[4]}, Expense: {sale[5]}")
        conn.close()

# CLI Interface
def run_cli():
    store = SnackStore()
    while True:
        print("\nSnack Store CLI")
        print("1. Add Product")
        print("2. Make Sale")
        print("3. View Stock")
        print("4. View Sales Summary")
        print("5. Exit")
        
        choice = input("Choose an option: ")
        if choice == '1':
            ean = input("Product EAN: ")
            name = input("Product Name: ")
            price = float(input("Product Price: "))
            stock = int(input("Product Stock: "))
            store.add_product(ean, name, price, stock)
        elif choice == '2':
            ean = input("Product EAN: ")
            quantity = int(input("Quantity to sell: "))
            store.make_sale(ean, quantity)
        elif choice == '3':
            store.view_stock()
        elif choice == '4':
            store.view_sales_summary()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

# Run the CLI if this script is executed
if __name__ == "__main__":
    run_cli()
