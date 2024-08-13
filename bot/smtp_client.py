import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from bot.config_manager import ConfigManager

class SMTPClient:
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the SMTPClient class.

        This constructor retrieves SMTP configuration settings using the ConfigManager.

        :param config_manager: An instance of ConfigManager to retrieve SMTP settings.
        """
        self.server = config_manager.get("smtp_server")
        self.port = config_manager.get("smtp_port")
        self.username = config_manager.get("smtp_username")
        self.password = config_manager.get("smtp_password")
        self.logger = logging.getLogger(__name__)

    def send_message(self, recipient_email, subject, text_message, html_message=None):
        """
        Send an email message to the specified recipient.

        :param recipient_email: The email address of the recipient.
        :param subject: The subject of the email.
        :param text_message: The plain text body of the email.
        :param html_message: The HTML body of the email (optional).
        :raises: Exception if the email fails to send.
        """
        try:
            # Set up the MIME structure
            msg = MIMEMultipart("alternative")
            msg['From'] = self.username
            msg['To'] = recipient_email
            msg['Subject'] = subject

            # Attach the plain text and HTML parts
            part1 = MIMEText(text_message, 'plain')
            msg.attach(part1)

            if html_message:
                part2 = MIMEText(html_message, 'html')
                msg.attach(part2)

            # Connect to the SMTP server and send the email
            with smtplib.SMTP(self.server, self.port) as server:
                self.logger.info(f"Connecting to SMTP server {self.server}:{self.port}")
                server.starttls()  # Secure the connection
                server.login(self.username, self.password)
                server.sendmail(self.username, recipient_email, msg.as_string())
                self.logger.info(f"Email sent to {recipient_email}")

        except smtplib.SMTPAuthenticationError:
            self.logger.error(f"SMTP Authentication failed for {self.username}")
            raise
        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP error occurred: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to send email to {recipient_email}: {e}")
            raise
