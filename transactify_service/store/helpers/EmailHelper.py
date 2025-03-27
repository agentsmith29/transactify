import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from django.core.exceptions import ObjectDoesNotExist

from store.webmodels.Customer import Customer
from transactify_service.settings import CONFIG

class EmailHelper:
    @staticmethod
    def send_email(card_number: str, subject: str, html_message: str, logger: logging.Logger = None):
        """
        Sends an email using the configured Gmail SMTP settings with an attached HTML file.

        Args:
            card_number (str): Customer's card number to look up email.
            subject (str): Email subject.
            html_message (str): HTML formatted message.
            logger (logging.Logger, optional): Logger instance for logging.

        Returns:
            bool: True if email was sent successfully, False otherwise.
        """
        if logger is None:
            logger = logging.getLogger(__name__)

        try:
            customer = Customer.objects.get(card_number=card_number)
        except ObjectDoesNotExist:
            logger.error("Can't send email. Customer not found.")
            return False

        try:
            # Email setup
            smtp_server = CONFIG.gmail_config.host
            smtp_port = CONFIG.gmail_config.port
            sender_email = CONFIG.gmail_config.host_user
            sender_password = CONFIG.gmail_config.host_password
            use_tls = CONFIG.gmail_config.use_tls

            friendly_name = CONFIG.webservice.FRIENDLY_NAME
            sender_formatted = f"{friendly_name} <{sender_email}>"

            msg = MIMEMultipart('alternative')
            msg["From"] = sender_formatted
            msg["To"] = customer.user.email
            msg["Subject"] = subject

            # Attach the HTML message as a file
            #html_attachment = MIMEApplication(html_message, _subtype="html")
            #html_attachment.add_header("Content-Disposition", "attachment", filename="message.html")
            #msg.attach(html_attachment)
            # Attach the HTML message as the main email content
            msg.attach(MIMEText(html_message, "html"))


            # Connect to SMTP server
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls() if use_tls else None
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, customer.user.email, msg.as_string())
            server.quit()

            logger.info(f"Email successfully sent to {customer.user.email}.")
            return True

        except Exception as e:
            logger.error(f"Error sending email to {customer.user.email}: {e}")
            return False

    import logging
import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.core.exceptions import ObjectDoesNotExist

from store.webmodels.Customer import Customer
from transactify_service.settings import CONFIG

class EmailHelper:
    @staticmethod
    def send_email(mail_address, subject: str, html_message: str, logger: logging.Logger = None):
        """
        Sends an email using the configured Gmail SMTP settings with an HTML message.

        Args:
            card_number (str): Customer's card number to look up email.
            subject (str): Email subject.
            html_message (str): HTML formatted message.
            logger (logging.Logger, optional): Logger instance for logging.

        Returns:
            bool: True if email was sent successfully, False otherwise.
        """
        if logger is None:
            logger = logging.getLogger(__name__)
        

        try:
            # Email setup
            smtp_server = CONFIG.gmail_config.host
            smtp_port = CONFIG.gmail_config.port
            sender_email = CONFIG.gmail_config.host_user
            sender_password = CONFIG.gmail_config.host_password
            use_tls = CONFIG.gmail_config.use_tls

            friendly_name = CONFIG.webservice.FRIENDLY_NAME
            sender_formatted = f"{friendly_name} <{sender_email}>"

            msg = MIMEMultipart("alternative")
            msg["From"] = sender_formatted
            
            
            msg["Subject"] = subject

            # Attach the HTML message as the main email content
            msg.attach(MIMEText(html_message, "html"))

            # Connect to SMTP server
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls() if use_tls else None
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, mail_address, msg.as_string())
            server.quit()

            logger.info(f"Email successfully sent to {mail_address}.")
            return True

        except Exception as e:
            logger.error(f"Error sending email to {mail_address}: {e}")
            return False

    @staticmethod
    def get_sent_email(customer: Customer, logger: logging.Logger = None):
        """
        Retrieves sent emails from Gmail for a customer based on their card number.

        Args:
            card_number (str): Customer's card number to look up email.
            logger (logging.Logger, optional): Logger instance for logging.

        Returns:
            list: A list of sent email messages.
        """
        if logger is None:
            logger = logging.getLogger(__name__)

        try:
            # IMAP setup
            imap_server = "imap.gmail.com"
            email_user = CONFIG.gmail_config.host_user  # Your email
            email_pass = CONFIG.gmail_config.host_password  # App Password
            
            # Connect to IMAP
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(email_user, email_pass)
            mail.select('"[Gmail]/Sent Mail"')  # Gmail's sent folder

            # Search for sent emails to the customer
            search_criteria = f'TO "{customer.user.email}"'
            result, data = mail.search(None, search_criteria)

            if result != "OK":
                logger.error("No emails found.")
                return []

            email_list = []
            for num in data[0].split():
                result, msg_data = mail.fetch(num, "(RFC822)")
                if result != "OK":
                    continue

                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                subject = msg["Subject"] or "No Subject"
                email_body = ""

                # Extract email body (HTML preferred)
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/html":
                            email_body = part.get_payload(decode=True).decode()
                            break
                else:
                    email_body = msg.get_payload(decode=True).decode()

                email_list.append({
                    "subject": subject,
                    "body": email_body,
                    "recipient": msg["To"],
                    "timestamp": msg["Date"]

                })

            mail.logout()
            logger.info(f"Retrieved {len(email_list)} sent emails for {customer.user.email}.")
            return email_list

        except Exception as e:
            logger.error(f"Error fetching sent emails for {customer.user.email}: {e}")
            return []

    @staticmethod
    def get_received_email(customer: Customer, logger: logging.Logger = None):
        """
        Retrieves received emails from Gmail for a customer based on their card number.

        Args:
            card_number (str): Customer's card number to look up email.
            logger (logging.Logger, optional): Logger instance for logging.

        Returns:
            list: A list of received email messages.
        """
        if logger is None:
            logger = logging.getLogger(__name__)

        try:
            # IMAP setup
            imap_server = "imap.gmail.com"
            email_user = CONFIG.gmail_config.host_user  # Your Gmail Address
            email_pass = CONFIG.gmail_config.host_password  # App Password
            
            # Connect to IMAP
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(email_user, email_pass)
            mail.select("INBOX")  # Select inbox folder

            # Search for emails received from your own email address (sent by customer)
            search_criteria = f'FROM "{customer.user.email}"'
            result, data = mail.search(None, search_criteria)

            if result != "OK":
                logger.error("No received emails found.")
                return []

            email_list = []
            for num in data[0].split():
                result, msg_data = mail.fetch(num, "(RFC822)")
                if result != "OK":
                    continue

                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                subject = msg["Subject"] or "No Subject"
                sender = msg["From"]
                timestamp = msg["Date"]
                email_body = ""

                # Extract email body (HTML preferred)
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/html":
                            email_body = part.get_payload(decode=True).decode()
                            break
                else:
                    email_body = msg.get_payload(decode=True).decode()

                email_list.append({
                    "subject": subject,
                    "sender": sender,
                    "timestamp": timestamp,
                    "body": email_body
                })

            mail.logout()
            logger.info(f"Retrieved {len(email_list)} received emails from {customer.user.email}.")
            return email_list

        except Exception as e:
            logger.error(f"Error fetching received emails from {customer.user.email}: {e}")
            return []