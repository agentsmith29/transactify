import os
import json
import requests
import traceback
from datetime import datetime
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from store.helpers.ManageStockHelper import StoreHelper
from transactify_service.HttpResponses import HTTPResponses
from store.webmodels.Customer import Customer
from store import StoreLogsDBHandler
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from config import Config

from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from django.contrib.auth.models import User
    

class ManageCustomersView(View, LoginRequiredMixin):
    """Class-based view to handle customer-related operations."""
    template_name = 'store/customers.html'

    def __init__(self):
        super().__init__()
        self.logger = StoreLogsDBHandler.setup_custom_logging('ManageCustomersView')
        self.conf: Config = settings.CONFIG

    def fetch_nfc_data(self):
        """Fetch NFC data synchronously using requests."""
        terminal_url = f"{self.conf.terminal.TERMINAL_SERVICE_URL}/api/read/nfc-blocking/"
        try:
            response = requests.get(terminal_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            self.logger.error(f"HTTP error while fetching NFC data: {e}")
            return {"status": "error", "message": f"HTTP error: {str(e)}"}
        except requests.Timeout as e:
            self.logger.error(f"Timeout error while fetching NFC data: {e}")
            return {"status": "error", "message": f"Timeout error: {str(e)}"}
        except requests.RequestException as e:
            self.logger.error(f"Request error while fetching NFC data: {e}")
            return {"status": "error", "message": f"Request error: {str(e)}"}

    def get_all_customers(self):
        """Returns all customers."""
        return Customer.objects.all()

    def delete_customer(self, data):
        """Delete a customer."""
        try:
            username = data.get('username')
            if not username:
                response = HTTPResponses.HTTP_STATUS_JSON_PARSE_ERROR('Missing required fields')
                data, status = response.json_data()
                return JsonResponse(data, status=status)
            user = User.objects.filter(username=username).first()
            customer = Customer.objects.filter(user=user).first()
            if not customer:
                response = HTTPResponses.HTTP_STATUS_CUSTOMER_NOT_FOUND(username)
                data, status = response.json_data()
                return JsonResponse(data, status=status)

            customer.delete()
            # also delete the user
            # user = User.objects.filter(username=username).first()

            response = HTTPResponses.HTTP_STATUS_CUSTOMER_DELETED(username)
            data, status = response.json_data()
            return JsonResponse(data, status=status)

        except Exception as e:
            self.logger.error(f"Error deleting customer: {e}")
            tb = traceback.format_exc()
            self.logger.error(f"Exception: {e}\n{tb}")
            response = HTTPResponses.HTTP_STATUS_CUSTOMER_DELETE_FAILED(username, e)
            data, status = response.json_data()
            return JsonResponse(data, status=status)
    
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        """Handle GET requests to display all customers."""
        customers = self.get_all_customers()
        return render(request, self.template_name, {'customers': customers})
        

    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        """Handle POST requests to add a new customer."""
        try:
            data = json.loads(request.body)
            header_cmd = request.headers.get('cmd')

            if header_cmd == "delete":
                return self.delete_customer(data)
            
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            balance = float(data.get('balance', 0))
            card_number = str(data.get('card_number'))

            if not all([first_name, last_name, email, card_number]):
                response = HTTPResponses.HTTP_STATUS_JSON_PARSE_ERROR('Missing required fields: first_name, last_name, email, card_number')
                data, status = response.json_data()
                return JsonResponse(data, status=status)
            
            # Check if the card_number is not empty or None
            if not card_number or card_number.strip() == "" or card_number == "None":
                response = HTTPResponses.HTTP_STATUS_JSON_PARSE_ERROR(f"Card {card_number} number cannot be empty")
                data, status = response.json_data()
                return JsonResponse(data, status=status)

            username = f"{first_name[0].lower()}.{last_name.lower()}"

        except Exception as e:
            self.logger.error(f"Error parsing input data: {e}")
            response = HTTPResponses.HTTP_STATUS_JSON_PARSE_ERROR(e)
            data, status = response.json_data()
            return JsonResponse(data, status=status)

        try:
            self.logger.info("Waiting for NFC card...")
            self.logger.info(f"NFC card number: {card_number}")

            response, customer = StoreHelper.create_new_customer(
                username, first_name, last_name, email, balance, card_number, self.logger
            )
            data, status = response.json_data()
            return JsonResponse(data, status=status)

        except Exception as e:
            self.logger.error("Error creating a new customer.")
            tb = traceback.format_exc()
            self.logger.error(f"Exception: {e}\n{tb}")
            response = HTTPResponses.HTTP_STATUS_CUSTOMER_CREATE_FAILED(username, e)
            data, status = response.json_data()
            return JsonResponse(data, status=status)
