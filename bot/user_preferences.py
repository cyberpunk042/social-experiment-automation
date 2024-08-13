import logging
from bot.config_manager import ConfigManager
from bot.database_client import DatabaseClient

class UserPreferences:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(UserPreferences, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the UserPreferences class.

        This constructor initializes the configuration manager and database client
        required for managing user preferences.

        :param config_manager: An instance of ConfigManager for retrieving default settings.
        """
        if hasattr(self, '_initialized') and self._initialized:
            return
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        self.db_client = DatabaseClient(config_manager)
        self.preferences = {}
        self._initialized = True

    def load_preferences(self, user_id):
        """
        Load preferences for a given user from the database or default settings.

        :param user_id: The ID of the user whose preferences are being loaded.
        """
        try:
            preferences = self.db_client.get_user_preferences(user_id)
            if preferences:
                self.preferences[user_id] = self._validate_preferences(preferences)
                self.logger.info(f"Loaded preferences for user {user_id}")
            else:
                self.logger.info(f"No preferences found for user {user_id}, using defaults.")
                self.preferences[user_id] = self._default_preferences()
        except Exception as e:
            self.logger.error(f"Failed to load preferences for user {user_id}: {e}")
            self.preferences[user_id] = self._default_preferences()

    def get_preferences(self, user_id):
        """
        Retrieve preferences for a user, loading them if not already in memory.

        :param user_id: The ID of the user whose preferences are being retrieved.
        :return: A dictionary of user preferences.
        """
        if user_id not in self.preferences:
            self.load_preferences(user_id)
        return self.preferences.get(user_id, self._default_preferences())

    def update_preferences(self, user_id, new_preferences):
        """
        Update the user's preferences in the database and in memory.

        :param user_id: The ID of the user whose preferences are being updated.
        :param new_preferences: A dictionary of new preferences to be updated.
        """
        try:
            validated_preferences = self._validate_preferences(new_preferences)
            self.db_client.update_user_preferences(user_id, validated_preferences)
            self.preferences[user_id] = validated_preferences
            self.logger.info(f"Updated preferences for user {user_id} to {validated_preferences}")
        except Exception as e:
            self.logger.error(f"Failed to update preferences for user {user_id}: {e}")

    def _default_preferences(self):
        """
        Return the default preferences from ConfigManager.

        :return: A dictionary of default preferences.
        """
        return {
            "notifications_enabled": self.config_manager.get("default_notifications_enabled", True),
            "response_style": self.config_manager.get("default_response_style", "friendly"),
            "content_tone": self.config_manager.get("default_content_tone", "neutral"),
            "content_frequency": self.config_manager.get("default_content_frequency", "daily"),
            "notification_method": self.config_manager.get("default_notification_method", "email"),
            "interaction_type": self.config_manager.get("default_interaction_type", "reactive"),
        }

    def _validate_preferences(self, preferences):
        """
        Validate and sanitize user preferences to ensure they conform to expected values.

        :param preferences: A dictionary of preferences to validate.
        :return: A sanitized dictionary of preferences.
        """
        if "notifications_enabled" not in preferences:
            preferences["notifications_enabled"] = self.config_manager.get("default_notifications_enabled", True)

        valid_response_styles = ["friendly", "formal", "casual"]
        if preferences.get("response_style") not in valid_response_styles:
            self.logger.warning(f"Invalid response style: {preferences.get('response_style')}, setting to default.")
            preferences["response_style"] = self.config_manager.get("default_response_style", "friendly")

        valid_content_tones = ["neutral", "positive", "negative"]
        if preferences.get("content_tone") not in valid_content_tones:
            self.logger.warning(f"Invalid content tone: {preferences.get('content_tone')}, setting to default.")
            preferences["content_tone"] = self.config_manager.get("default_content_tone", "neutral")

        valid_content_frequencies = ["daily", "weekly", "monthly"]
        if preferences.get("content_frequency") not in valid_content_frequencies:
            self.logger.warning(f"Invalid content frequency: {preferences.get('content_frequency')}, setting to default.")
            preferences["content_frequency"] = self.config_manager.get("default_content_frequency", "daily")

        valid_notification_methods = ["email", "sms", "none"]
        if preferences.get("notification_method") not in valid_notification_methods:
            self.logger.warning(f"Invalid notification method: {preferences.get('notification_method')}, setting to default.")
            preferences["notification_method"] = self.config_manager.get("default_notification_method", "email")

        valid_interaction_types = ["proactive", "reactive", "neutral"]
        if preferences.get("interaction_type") not in valid_interaction_types:
            self.logger.warning(f"Invalid interaction type: {preferences.get('interaction_type')}, setting to default.")
            preferences["interaction_type"] = self.config_manager.get("default_interaction_type", "reactive")

        return preferences
