import logging
from config_manager import ConfigManager
from database_client import DatabaseClient

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
        self.tone = 'reserved'  # Default tone

    def set_tone(self, tone):
        self.tone = tone

    def get_tone(self):
        return self.tone
    
    def get_tone_directive(self):
        """
        Retrieve the user's preferred tone directive for generating content.

        Returns:
            str: The preferred tone directive (e.g., "reserved", "vulgar", "bold", "humble").
        """
        # Example implementation, defaulting to "reserved"
        return self.tone_directive if hasattr(self, 'tone_directive') else "reserved"

    def select_preferred_caption(self, captions):
        """
        Select the most appropriate caption from a list based on user preferences.

        Args:
            captions (list): A list of caption dictionaries retrieved from the database.

        Returns:
            str: The text of the selected caption.

        Raises:
            ValueError: If no suitable captions are found.
        """
        # User preferences
        preferred_tags = self.tags
        preferred_length = self.length
        preferred_category = self.category
        preferred_tone = self.tone
        audience = self.audience  # Additional audience targeting
        language = self.language  # Multi-language support

        # Filter captions based on user preferences
        filtered_captions = [
            caption for caption in captions
            if (not preferred_tags or any(tag in caption['tags'] for tag in preferred_tags)) and
            (not preferred_length or caption['length'] == preferred_length) and
            (not preferred_category or caption['category'] == preferred_category) and
            (not preferred_tone or caption['tone'] == preferred_tone) and
            (not audience or caption.get('audience') == audience) and
            (not language or caption.get('language') == language)
        ]

        if not filtered_captions:
            raise ValueError("No suitable captions found based on the given preferences.")

        # Rank captions by engagement or other metrics
        ranked_captions = sorted(
            filtered_captions,
            key=lambda c: (c['engagement']['likes'] + c['engagement']['shares'] + c['engagement']['comments']),
            reverse=True
        )

        # Select the top-ranked caption
        selected_caption = ranked_captions[0]['text'] if ranked_captions else None

        if not selected_caption:
            raise ValueError("No suitable captions found after filtering and ranking.")

        return selected_caption


    def load_preferences(self):
        """
        Load preferences from the database or default settings.

        Since this is a POC with a single user, preferences are loaded once.
        """
        try:
            preferences = self.db_client.get_user_preferences()
            if preferences:
                self.preferences = self._validate_preferences(preferences)
                self.logger.info(f"Loaded preferences")
            else:
                self.logger.info(f"No preferences found, using defaults.")
                self.preferences = self._default_preferences()
        except Exception as e:
            self.logger.error(f"Failed to load preferences: {e}")
            self.preferences = self._default_preferences()

    def get_preferences(self):
        """
        Retrieve preferences, loading them if not already in memory.

        :return: A dictionary of user preferences.
        """
        if not self.preferences:
            self.load_preferences()
        return self.preferences

    def update_preferences(self, new_preferences):
        """
        Update the user's preferences in the database and in memory.

        :param new_preferences: A dictionary of new preferences to be updated.
        """
        try:
            validated_preferences = self._validate_preferences(new_preferences)
            self.db_client.update_user_preferences(validated_preferences)
            self.preferences = validated_preferences
            self.logger.info(f"Updated preferences to {validated_preferences}")
        except Exception as e:
            self.logger.error(f"Failed to update preferences: {e}")

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
            "comment_response_style": self.config_manager.get("default_comment_response_style", "friendly"),
            "comment_content_tone": self.config_manager.get("default_comment_content_tone", "positive"),
            "comment_interaction_type": self.config_manager.get("default_comment_interaction_type", "proactive"),
            "reply_response_style": self.config_manager.get("default_reply_response_style", "formal"),
            "reply_content_tone": self.config_manager.get("default_reply_content_tone", "neutral"),
            "reply_interaction_type": self.config_manager.get("default_reply_interaction_type", "reactive"),
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

        # Validate specific comment preferences
        if preferences.get("comment_response_style") not in valid_response_styles:
            self.logger.warning(f"Invalid comment response style: {preferences.get('comment_response_style')}, setting to default.")
            preferences["comment_response_style"] = self.config_manager.get("default_comment_response_style", "friendly")

        if preferences.get("comment_content_tone") not in valid_content_tones:
            self.logger.warning(f"Invalid comment content tone: {preferences.get('comment_content_tone')}, setting to default.")
            preferences["comment_content_tone"] = self.config_manager.get("default_comment_content_tone", "positive")

        if preferences.get("comment_interaction_type") not in valid_interaction_types:
            self.logger.warning(f"Invalid comment interaction type: {preferences.get('comment_interaction_type')}, setting to default.")
            preferences["comment_interaction_type"] = self.config_manager.get("default_comment_interaction_type", "proactive")

        # Validate specific reply preferences
        if preferences.get("reply_response_style") not in valid_response_styles:
            self.logger.warning(f"Invalid reply response style: {preferences.get('reply_response_style')}, setting to default.")
            preferences["reply_response_style"] = self.config_manager.get("default_reply_response_style", "formal")

        if preferences.get("reply_content_tone") not in valid_content_tones:
            self.logger.warning(f"Invalid reply content tone: {preferences.get('reply_content_tone')}, setting to default.")
            preferences["reply_content_tone"] = self.config_manager.get("default_reply_content_tone", "neutral")

        if preferences.get("reply_interaction_type") not in valid_interaction_types:
            self.logger.warning(f"Invalid reply interaction type: {preferences.get('reply_interaction_type')}, setting to default.")
            preferences["reply_interaction_type"] = self.config_manager.get("default_reply_interaction_type", "reactive")

        return preferences
