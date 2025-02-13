
# get the absolut path from the current file
import os
import sys
_filepwd = os.path.dirname(os.path.realpath(__file__))

from store.helpers.EmailHelper import EmailHelper

class MailTemplate:

    @staticmethod               
    def send_mail_template_purchase(card_number, order_num, buyer, purchased_item, total, date, store, logger):
        _template = f"{_filepwd}/purchase.html"
        with open(_template, "r", encoding="utf-8") as file:
            template = file.read()
        
        email_content = template.replace("{{ order_num }}", str(order_num)) \
                                .replace("{{ buyer }}", buyer) \
                                .replace("{{ purchased_item }}", purchased_item) \
                                .replace("{{ total }}", str(total)) \
                                .replace("{{ date }}", date) \
                                .replace("{{ store }}", str(store))
        
        EmailHelper.send_email(card_number=card_number, 
                    subject="Thank you for your purchase!", 
                    html_message=email_content,
                    logger=logger)
