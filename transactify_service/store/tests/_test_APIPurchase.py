from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock
from store.webmodels.Customer import Customer
from store.helpers.ManageStockHelper import StoreHelper

class CustomerPurchaseAPIViewTest(APITestCase):
    def setUp(self):
        self.url = '/api/customer-purchase/'  # Replace with the actual URL
        self.valid_payload = {
            'ean': '1234567890123',
            'quantity': 2,
            'card_number': '1234567890'
        }

    @patch('store.helpers.ManageStockHelper.customer_purchase')
    def test_valid_purchase(self, mock_customer_purchase):
        """Test a valid purchase request."""
        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.data = {"success": True, "message": "Purchase successful."}
        mock_customer_purchase.return_value = (mock_response, MagicMock(spec=Customer))

        response = self.client.post(self.url, data=self.valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("success", response.data)
        self.assertTrue(response.data["success"])

    def test_missing_fields(self):
        """Test request with missing required fields."""
        payload = {
            'ean': '1234567890123',
            # 'quantity' is missing
            'card_number': '1234567890'
        }
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "All fields (ean, quantity, card_number) are required.")

    def test_invalid_quantity_non_integer(self):
        """Test request with non-integer quantity."""
        payload = {
            'ean': '1234567890123',
            'quantity': 'invalid',
            'card_number': '1234567890'
        }
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertIn("Invalid data for quantity", response.data["error"])

    def test_invalid_quantity_negative(self):
        """Test request with negative quantity."""
        payload = {
            'ean': '1234567890123',
            'quantity': -5,
            'card_number': '1234567890'
        }
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Quantity must be a positive integer.")

    @patch('store.helpers.ManageStockHelper.customer_purchase')
    def test_purchase_helper_exception(self, mock_customer_purchase):
        """Test exception raised by StoreHelper.customer_purchase."""
        mock_customer_purchase.side_effect = Exception("Test exception")

        response = self.client.post(self.url, data=self.valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)
        self.assertIn("An error occurred during the purchase", response.data["error"])

    @patch('store.helpers.ManageStockHelper.customer_purchase')
    def test_purchase_helper_returns_none(self, mock_customer_purchase):
        """Test StoreHelper.customer_purchase returning None."""
        mock_customer_purchase.return_value = (None, None)

        response = self.client.post(self.url, data=self.valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Unexpected error: No response from ManageStockHelper.")

    def test_invalid_json(self):
        """Test request with invalid JSON body."""
        response = self.client.post(self.url, data="Invalid JSON", content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertIn("Invalid JSON format", response.data["error"])
