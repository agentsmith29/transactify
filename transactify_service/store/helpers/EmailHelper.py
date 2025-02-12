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
            html_attachment = MIMEApplication(html_message, _subtype="html")
            html_attachment.add_header("Content-Disposition", "attachment", filename="message.html")
            msg.attach(html_attachment)

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
