import os
import json
import requests
import traceback
from datetime import datetime

from store.webmodels.Customer import Customer

from django.http import JsonResponse
from django.views import View
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.utils.decorators import method_decorator

from store.helpers.ManageStockHelper import StoreHelper
from asgiref.sync import sync_to_async
import httpx

from ..webmodels.CustomerDeposit import CustomerDeposit
#from ..webmodels.CustomerBalance import CustomerBalance


from django.views.decorators.csrf import csrf_protect, csrf_exempt, ensure_csrf_cookie


from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from store import StoreLogsDBHandler

from transactify_service.HttpResponses import HTTPResponses


#from ..apps import hwcontroller
@method_decorator(login_required, name='dispatch')
class ManageCustomersView(View):
    """Class-based view to handle customer-related operations."""
    template_name = 'store/customers.html'

    def __init__(self):
        super().__init__()
        self.logger = StoreLogsDBHandler.setup_custom_logging('ManageCustomersView')

    def get_all_customers(self):
        """Returns all customers."""
        return Customer.objects.all()
    
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        """Handle GET requests to display all customers."""
        customers = self.get_all_customers()
        return render(request, self.template_name, {"customers": customers})
    
    async def fetch_nfc_data(self):
        """Fetch NFC data asynchronously using httpx."""
        terminal_url = f"{os.getenv('TERMINAL_SERVICES')}/api/read/nfc-blocking/"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(terminal_url, timeout=10)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error while fetching NFC data: {e}")
            return {"status": "error", "message": f"HTTP error: {str(e)}"}
        except httpx.RequestError as e:
            self.logger.error(f"Request error while fetching NFC data: {e}")
            return {"status": "error", "message": f"Request error: {str(e)}"}
        
    @method_decorator(csrf_protect)
    async def post(self, request):
        """Handle POST requests to add a new customer."""     
        
        try:
            data = json.loads(request.body)
            self.logger.debug(f"Post request recieved: {data}")
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            # convert balance to Decimal
            balance = float(data.get('balance'))

            self.logger.debug(f"Received data: {first_name}, {last_name}, {email}, {balance}")
            # Validate the required fields
            if not first_name or not last_name or not email or balance is None:
                response = HTTPResponses.HTTP_STATUS_JSON_PARSE_ERROR('Missing required fields')
                data, status = response.json_data()
                # --------------------------------------
                return JsonResponse(data, status=status)
            
            username = f"{first_name[0].lower()}.{last_name.lower()}"
            self.logger.debug(f"Generated username: {username}")
        except Exception as e:
            response = HTTPResponses.HTTP_STATUS_JSON_PARSE_ERROR(e)
            data, status = response.json_data()
            # --------------------------------------
            return JsonResponse(data, status=status)


        try:
            # Trigger NFC read
            time = datetime.now()
            # Trigger NFC read
            self.logger.info("Waiting for NFC card...")
            time_start = datetime.now()
            nfc_data = await self.fetch_nfc_data(request)

            if nfc_data.get("status") == "error":
                return JsonResponse(nfc_data, status=500)

            card_number = nfc_data.get("id")
            content = nfc_data.get("content")


            time_stop = datetime.now()
            time_delta = time_stop - time
            self.logger.debug(f"Waited for NFC card for: {time_delta}.")
            self.logger.info(f"Card number: {card_number}, Content: {content}.")
            # --------------------------------------
            # Create and save the new customer
             # Create and save the new customer
            response, customer = StoreHelper.create_new_customer(
                username, first_name, last_name, email, balance, card_number, self.logger
            )
            data, status = response.json_data()
            # --------------------------------------
            return JsonResponse(data, status=status)
        except Exception as e:
            self.logger.error(f"Error creating a new customer.")
            tb = traceback.format_exc()
            #self.logger.error(f"Exception: {e}\n{tb}")
            data, status = HTTPResponses.HTTP_STATUS_CUSTOMER_CREATE_FAILED(username, e).json_data()
            return JsonResponse(data, status=status)
