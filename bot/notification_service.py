import logging
from bot.smtp_client import SMTPClient
from bot.user_preferences import UserPreferences

class NotificationService:
    def __init__(self, smtp_client: SMTPClient, user_preferences: UserPreferences):
        self.logger = logging.getLogger(__name__)
        self.smtp_client = smtp_client
        self.user_preferences = user_preferences

    def send_notification(self, user_id: str, subject: str, message: str):
        try:
            user_prefs = self.user_preferences.get_preferences(user_id)  # Fetch and validate preferences
            notification_method = user_prefs.get("notification_method")

            # Send notification based on the preferred method
            if notification_method == "email":
                user_email = user_prefs.get("email")
                self.smtp_client.send_message(user_email, subject, message)
                self.logger.info(f"Email notification sent to {user_email}.")
            elif notification_method == "sms":
                # Implement SMS notification logic if needed
                self.logger.info(f"SMS notification sent to user {user_id}.")
            else:
                self.logger.info(f"No notification sent. Notification method set to 'none' for user {user_id}.")

        except Exception as e:
            self.logger.error(f"Failed to send notification to user {user_id}: {e}")
