from django.test import TestCase, Client
from django.contrib.auth.models import User
from store.webmodels.Customer import Customer
from store.webmodels.StoreProduct import StoreProduct
from django.urls import reverse
from decimal import Decimal

class ManageProductsViewTest(TestCase):

    def setUp(self):
        # Create test user and log in
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        # Create multiple test products
        self.products = [
            StoreProduct.objects.create(
                ean=f"12345{i}",
                name=f"Product{i}",
                resell_price=Decimal(f"10.{i}")
            ) for i in range(5)
        ]

    def test_get_all_products(self):
        # Test if the view fetches all products
        response = self.client.get(reverse('manage_products'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/manage_products.html')

        # Check if all products are present in the context
        products_from_context = response.context['products']
        self.assertEqual(len(products_from_context), len(self.products))

    def test_post_create_product(self):
        # Test if a new product is created
        new_product_data = {
            'product_ean': '99999',
            'product_name': 'New Product',
            'resell_price': '19.99',
        }
        response = self.client.post(reverse('manage_products'), data=new_product_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation

        # Verify the new product exists in the database
        new_product = StoreProduct.objects.filter(ean='99999').first()
        self.assertIsNotNone(new_product)
        self.assertEqual(new_product.name, 'New Product')
        self.assertEqual(new_product.resell_price, Decimal('19.99'))

    def test_post_delete_product(self):
        # Test if a product is deleted
        product_to_delete = self.products[0]
        response = self.client.post(reverse('manage_products'), data={'delete_ean': product_to_delete.ean})
        self.assertEqual(response.status_code, 302)  # Redirect after successful deletion

        # Verify the product no longer exists in the database
        deleted_product = StoreProduct.objects.filter(ean=product_to_delete.ean).first()
        self.assertIsNone(deleted_product)

    def test_post_create_product_missing_fields(self):
        # Test creating a product with missing fields
        new_product_data = {
            'product_ean': '99999',
            'product_name': '',  # Missing product name
            'resell_price': '19.99',
        }
        response = self.client.post(reverse('manage_products'), data=new_product_data)
        self.assertEqual(response.status_code, 400)  # Bad request
        self.assertContains(response, "Missing required fields")

    def test_post_create_product_invalid_price(self):
        # Test creating a product with an invalid price
        new_product_data = {
            'product_ean': '99999',
            'product_name': 'Invalid Product',
            'resell_price': 'invalid_price',  # Invalid price
        }
        response = self.client.post(reverse('manage_products'), data=new_product_data)
        self.assertEqual(response.status_code, 400)  # Bad request
        self.assertContains(response, "Invalid price format")

    def test_post_create_duplicate_product(self):
        # Test creating a product with a duplicate EAN
        duplicate_product_data = {
            'product_ean': self.products[0].ean,  # Duplicate EAN
            'product_name': 'Duplicate Product',
            'resell_price': '15.99',
        }
        response = self.client.post(reverse('manage_products'), data=duplicate_product_data)
        self.assertEqual(response.status_code, 200)  # Nothing should happen
        product = StoreProduct.objects.get(ean=duplicate_product_data['product_ean'])
        # All fields should remain the same
        self.assertEqual(product, self.products[0].name, 'Product0')
        self.assertEqual(self.products[0].resell_price, Decimal('10.0'))
        self.assertEqual(StoreProduct.objects.filter(ean=self.products[0].ean).count(), 1)

    def test_post_delete_nonexistent_product(self):
        # Test deleting a product that does not exist
        response = self.client.post(reverse('manage_products'), data={'delete_ean': '00000'})  # Non-existent EAN
        self.assertEqual(response.status_code, 404)  # Not found
        self.assertContains(response, "Product not found")

    def test_post_create_product_large_price(self):
        # Test creating a product with an unreasonably large price
        new_product_data = {
            'product_ean': '88888',
            'product_name': 'Expensive Product',
            'resell_price': '99999999.99',  # Large price
        }
        response = self.client.post(reverse('manage_products'), data=new_product_data)
        self.assertEqual(response.status_code, 400)  # Bad request
        self.assertContains(response, "Price exceeds allowed limit")

    def test_post_create_product_zero_or_negative_price(self):
        # Test creating a product with zero or negative price
        negative_price_data = {
            'product_ean': '77777',
            'product_name': 'Negative Price Product',
            'resell_price': '-10.99',  # Negative price
        }
        zero_price_data = {
            'product_ean': '66666',
            'product_name': 'Zero Price Product',
            'resell_price': '0.00',  # Zero price
        }

        negative_response = self.client.post(reverse('manage_products'), data=negative_price_data)
        self.assertEqual(negative_response.status_code, 400)  # Bad request
        self.assertContains(negative_response, "Price must be positive")

        zero_response = self.client.post(reverse('manage_products'), data=zero_price_data)
        self.assertEqual(zero_response.status_code, 400)  # Bad request
        self.assertContains(zero_response, "Price must be greater than zero")
