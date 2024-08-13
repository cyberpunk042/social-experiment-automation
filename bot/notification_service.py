# bot/notification_service.py
import logging
from messaging_client import MessagingClient # TODO: Replace with something valid. SMTP Client Class with module.

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, messaging_client: MessagingClient):
        self.messaging_client = messaging_client

    def send_notification(self, user_id: str, message: str):
        # Function to send a notification to a user
        try:
            self.messaging_client.send_message(user_id, message)
            logger.info(f"Notification sent to user {user_id}.")
        except Exception as e:
            logger.error(f"Failed to send notification to user {user_id}: {e}")
