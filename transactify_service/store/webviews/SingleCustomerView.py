import json

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt, ensure_csrf_cookie

from store.webmodels.Customer import Customer

from ..webmodels.CustomerDeposit import CustomerDeposit
from ..webmodels.CustomerPurchase import CustomerPurchase
from store.helpers.ManageStockHelper import StoreHelper
from store import StoreLogsDBHandler 


from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import models
from datetime import datetime, timedelta

import traceback
from transactify_service.settings import CONFIG
import logging

from store.helpers.EmailHelper import EmailHelper
from store.mail_html_templates.MailTemplate import MailTemplate
from store.helpers.EmailHelper import EmailHelper

#from ..apps import hwcontroller
@method_decorator(login_required, name='dispatch')
class SingleCustomerView(View):
    template_name = 'store/customer.html'

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f"{CONFIG.webservice.SERVICE_NAME}.webviews.{self.__class__.__name__}")
        super().__init__(**kwargs)
    

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, card_number=None):
        """+
        Handle GET requests to display customer details and deposit history.
        """
        if card_number is None:
            card_number = request.GET.get('card_number')

        customer = get_object_or_404(Customer, card_number=card_number)
        balance = customer.balance

        _sent_mails = EmailHelper.get_sent_email(card_number=card_number, logger=self.logger)
        _recieved_mails = EmailHelper.get_received_email(card_number=card_number, logger=self.logger)
        print(f"Sent mails: {_sent_mails}")
        
        return render(request, self.template_name, {
            'auth_user': request.user,
            'customer': customer,
            #'balance': balance,
            #'total_deposits': customer.total_deposits,
            #'total_purchases': customer.total_purchases,
            'deposits': customer.get_deposits(),
            'total_deposits_amount': customer.get_total_deposit_amount(),
            'purchases': customer.get_purchases(),
            'total_purchases_amount': customer.get_total_purchase_amount(),
            'store_profit': customer.get_generated_profit(),
            'store_profit_change_percent': customer.get_monthly_generated_profit_change(),
            # percetgae change in the last month
            'deposit_change_percent': customer.get_monthly_deposit_percentage_change(),
            'purchase_change_percent': customer.get_monthly_purchase_percentage_change(),
            'sent_emails': _sent_mails,
            'recieved_emails': _recieved_mails,
            #'chart_data': customer.chart_data
        })
   

    def post(self, request, card_number=None):
        """
        Handle POST requests to update the customer's balance by adding a deposit.
        """
        try:
            # check the header for field cmd
            if 'cmd' in request.headers:
                cmd = request.headers['cmd']
            else:
                cmd = "deposit"

            data = json.loads(request.body)
            self.logger.debug(f"Post request recieved: {data}")


            if cmd == "deposit":
                amount = data.get('deposit_amount')
                if not amount or float(amount) <= 0:
                    return JsonResponse({'error': 'Invalid amount'}, status=400)

                # Fetch the customer
                customer = get_object_or_404(Customer, card_number=card_number)
                response, customer_deposit = StoreHelper.customer_add_deposit(customer, amount, self.logger )
                return JsonResponse({'message': 'Deposit successful'}, status=200)
            elif cmd == "update":
                first_name = data.get("first_name")
                last_name = data.get("last_name")
                email = data.get("email")
                password = data.get("password")

                if not card_number:
                    msg = "Customer ID is required for updating details."
                    self.logger.error(msg)
                    return JsonResponse({'error': 'Invalid JSON data'}, status=400)

                response, updated_customer = StoreHelper.update_customer_details(
                    card_number=card_number,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password,
                    logger=self.logger
                )


                if "config" in data:
                    config = data.get("config")
                    auto_deposit = config.get("auto_deposit")
                    response, updated_customer = StoreHelper.update_customer_config(
                        card_number=card_number,
                        auto_deposit=bool(auto_deposit),
                        logger=self.logger
                )
                data, status = response.json_data()

                return JsonResponse(data=data, status=status)
            elif cmd == "send_email":
                subject = data.get('subject')
                html_message = data.get('html_message')
                
                if not subject or not html_message:
                    return JsonResponse({'error': 'Subject and message cannot be empty'}, status=400)
                EmailHelper.send_email(card_number=card_number, subject=subject, html_message=html_message, logger=self.logger)
                return JsonResponse({'success': True, 'message': 'Email sent successfully'}, status=200)

        except json.JSONDecodeError as jse:
            self.logger.error(f"Invalid JSON data: {jse}")
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            self.logger.error(f"An error occurred: {str(e)}")
            self.logger.error(f"Traceback:\n{traceback.format_exc()}\n")
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
