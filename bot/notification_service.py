# bot/notification_service.py
import logging
from bot.smtp_client import SMTPClient

class NotificationService:
    def __init__(self, smtp_client: SMTPClient):
        self.logger = logging.getLogger(__name__)
        self.smtp_client = smtp_client

    def send_notification(self, user_email: str, subject: str, message: str):
        try:
            self.smtp_client.send_message(user_email, subject, message)
            self.logger.info(f"Notification sent to user {user_email}.")
        except Exception as e:
            self.logger.error(f"Failed to send notification to user {user_email}: {e}")
