
# get the absolut path from the current file
import os
import sys
_filepwd = os.path.dirname(os.path.realpath(__file__))

from store.webmodels.Customer import Customer

from store.helpers.EmailHelper import EmailHelper
from django.contrib.auth.models import User

class MailTemplate:

    @staticmethod               
    def send_mail_template_purchase(customer, order_num, purchased_item, total, date, store, 
                                    logger, send_to_admin=True):
        _template = f"{_filepwd}/template_purchase.html"
        with open(_template, "r", encoding="utf-8") as file:
            template = file.read()
        
        email_content = template.replace("{{ order_num }}", str(order_num)) \
                                .replace("{{ buyer }}", f"{customer.user.first_name} {customer.user.last_name}") \
                                .replace("{{ purchased_item }}", purchased_item) \
                                .replace("{{ total }}", str(total)) \
                                .replace("{{ date }}", date) \
                                .replace("{{ store }}", str(store))
    
        if customer.config.email_enabled and customer.config.email_on_purchase:
            EmailHelper.send_email(mail_address=customer.user.email, 
                        subject="Thank you for your purchase!", 
                        html_message=email_content,
                        logger=logger)
            
        if send_to_admin:
            admin = User.objects.get(username="admin")
            EmailHelper.send_email_threaded(mail_address=admin.email, 
                   subject="Thank you for your purchase!", 
                    html_message=email_content,
                    logger=logger)

    @staticmethod               
    def send_mail_template_new_deposit(customer, balanced_added, balance, date, store, 
                                       logger, send_to_admin=True):
        _template = f"{_filepwd}/template_balance_updated.html"
        with open(_template, "r", encoding="utf-8") as file:
            template = file.read()
        
        email_content = template.replace("{{ buyer }}", f"{customer.user.first_name} {customer.user.last_name}") \
                                .replace("{{ balanced_added }}", str(balanced_added)) \
                                .replace("{{ balance }}", str(balance)) \
                                .replace("{{ date }}", date) \
                                .replace("{{ store }}", str(store))
        
        if customer.config.email_enabled and customer.config.email_on_deposit:
            EmailHelper.send_email_threaded(mail_address=customer.user.email, 
                        subject=f"New Deposit: {balanced_added}€ added", 
                        html_message=email_content,
                        logger=logger)
            
        if send_to_admin:
            admin = User.objects.get(username="admin")
            EmailHelper.send_email_threaded(mail_address=admin.email, 
                    subject=f"New Deposit: {balanced_added}€ added (Admin Mirror)", 
                    html_message=email_content,
                    logger=logger)
