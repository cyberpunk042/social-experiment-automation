import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from bot.config_manager import ConfigManager

class SMTPClient:
    def __init__(self, config_manager: ConfigManager):
        self.server = config_manager.get("smtp_server")
        self.port = config_manager.get("smtp_port")
        self.username = config_manager.get("smtp_username")
        self.password = config_manager.get("smtp_password")
        self.logger = logging.getLogger(__name__)

    def send_message(self, recipient_email, subject, message):
        try:
            # Set up the MIME
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = recipient_email
            msg['Subject'] = subject

            # Attach the message body
            msg.attach(MIMEText(message, 'plain'))

            # Connect to the SMTP server
            with smtplib.SMTP(self.server, self.port) as server:
                server.starttls()  # Secure the connection
                server.login(self.username, self.password)
                server.sendmail(self.username, recipient_email, msg.as_string())

            self.logger.info(f"Email sent to {recipient_email}")
        except Exception as e:
            self.logger.error(f"Failed to send email to {recipient_email}: {e}")
            raise
