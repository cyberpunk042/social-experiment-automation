import logging
from config_manager import ConfigManager
from database_client import DatabaseClient

class UserPreferences:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(UserPreferences, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_manager: ConfigManager, database_client: DatabaseClient, user_id: int):
        """
        Initialize the UserPreferences class.

        This constructor initializes the configuration manager and database client
        required for managing user preferences.

        :param config_manager: An instance of ConfigManager for retrieving default settings.
        :param database_client: An instance of DatabaseClient for interacting with the database.
        :param user_id: The ID of the user whose preferences are being managed.
        """
        if hasattr(self, '_initialized') and self._initialized:
            return
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        self.db_client = database_client
        self.user_id = user_id
        self.preferences = {}
        self._initialized = True

        # Initialize attributes with default values or from loaded preferences
        self.load_preferences()

        self.notifications_enabled = self.preferences.get('notifications_enabled', True)
        self.response_style = self.preferences.get('response_style', 'friendly')
        self.content_tone = self.preferences.get('content_tone', 'neutral')
        self.content_frequency = self.preferences.get('content_frequency', 'daily')
        self.notification_method = self.preferences.get('notification_method', 'email')
        self.interaction_type = self.preferences.get('interaction_type', 'reactive')

        # Additional preferences
        self.comment_response_style = self.preferences.get('comment_response_style', 'friendly')
        self.comment_content_tone = self.preferences.get('comment_content_tone', 'positive')
        self.comment_interaction_type = self.preferences.get('comment_interaction_type', 'proactive')
        self.reply_response_style = self.preferences.get('reply_response_style', 'formal')
        self.reply_content_tone = self.preferences.get('reply_content_tone', 'neutral')
        self.reply_interaction_type = self.preferences.get('reply_interaction_type', 'reactive')

        # Post preferences
        self.tags = self.preferences.get('tags', [])
        self.length = self.preferences.get('length', 'short')
        self.category = self.preferences.get('category', 'general')
        self.audience = self.preferences.get('audience', 'general')
        self.language = self.preferences.get('language', 'en')
        self.tone = self.preferences.get('tone', 'reserved')

    def load_preferences(self):
        """
        Load preferences from the database or prompt the user to enter them.
        """
        try:
            if not self.db_client.check_table_exists('user_preferences'):
                self.logger.warning("Table 'user_preferences' does not exist. It will be created.")
                self.db_client.create_table_user_preferences()

            preferences = self.db_client.get_user_preferences(self.user_id)
            if preferences:
                self.preferences = self._validate_preferences(preferences[0])
                self.logger.info(f"Loaded preferences for user_id {self.user_id}")
            else:
                self.logger.warning(f"No user preferences found for user_id: {self.user_id}")
                self.preferences = self.prompt_for_preferences()
                self.db_client.update_user_preferences(self.user_id, self.preferences)
        except Exception as e:
            self.logger.error(f"Failed to load preferences: {e}")
            self.preferences = self._default_preferences()

    def prompt_for_preferences(self):
        """
        Prompt the user in the terminal to enter their preferences.

        :return: A dictionary of user preferences.
        """
        def input_with_default(prompt, default):
            return input(f"{prompt} [{default}]: ").strip() or default

        preferences = {}
        preferences["notifications_enabled"] = input_with_default("Enable notifications (yes/no)", "no") == "yes"
        preferences["response_style"] = input_with_default("Response style (friendly/formal/casual)", "friendly")
        preferences["content_tone"] = input_with_default("Content tone (neutral/positive/negative)", "neutral")
        preferences["content_frequency"] = input_with_default("Content frequency (daily/weekly/monthly)", "daily")
        preferences["notification_method"] = input_with_default("Notification method (email/sms/none)", "email")
        preferences["interaction_type"] = input_with_default("Interaction type (proactive/reactive/neutral)", "neutral")

        # Additional preferences
        preferences["comment_response_style"] = input_with_default("Comment response style (friendly/formal/casual)", "friendly")
        preferences["comment_content_tone"] = input_with_default("Comment content tone (neutral/positive/negative)", "positive")
        preferences["comment_interaction_type"] = input_with_default("Comment interaction type (proactive/reactive/neutral)", "proactive")
        preferences["reply_response_style"] = input_with_default("Reply response style (friendly/formal/casual)", "formal")
        preferences["reply_content_tone"] = input_with_default("Reply content tone (neutral/positive/negative)", "neutral")
        preferences["reply_interaction_type"] = input_with_default("Reply interaction type (proactive/reactive/neutral)", "reactive")

        # Post preferences
        preferences["tags"] = input_with_default("Tags (comma-separated)", "").split(',')
        preferences["length"] = input_with_default("Post length (short/medium/long)", "short")
        preferences["category"] = input_with_default("Post category", "general")
        preferences["audience"] = input_with_default("Audience", "general")
        preferences["language"] = input_with_default("Language", "en")
        preferences["tone"] = input_with_default("Tone (reserved/bold/humble)", "reserved")

        self.logger.debug(f"User-entered preferences: {preferences}")

        return self._validate_preferences(preferences)

    def select_preferred_caption(self, captions, generated_captions):
        """
        Select the most appropriate caption from a list based on user preferences, excluding already generated captions.
        
        Args:
            captions (list): A list of caption dictionaries retrieved from the database.
            generated_captions (list): A list of generated caption dictionaries to be excluded, containing the caption_id.
        
        Returns:
            str: The text of the selected caption.
        
        Raises:
            ValueError: If no suitable captions are found.
        """
        
        def filter_captions(captions, tags=None, length=None, category=None, tone=None):
            return [
                caption for caption in captions
                if (not tags or any(tag.strip() in caption.get('tags', '').split(',')) for tag in tags) and
                (not length or caption.get('length') == length) and
                (not category or caption.get('category') == category) and
                (not tone or caption.get('tone') == tone)
            ]
        
        # Exclude already generated captions
        generated_caption_ids = {gen_caption['caption_id'] for gen_caption in generated_captions}
        captions = [caption for caption in captions if caption.get('id') not in generated_caption_ids]
        
        # Step 1: Try exact match
        filtered_captions = filter_captions(captions, self.tags, self.length, self.category, self.tone)
        
        # Step 2: Relax criteria (ignore category)
        if not filtered_captions:
            filtered_captions = filter_captions(captions, self.tags, self.length, None, self.tone)
        
        # Step 3: Further relax criteria (ignore category and tone)
        if not filtered_captions:
            filtered_captions = filter_captions(captions, self.tags, self.length, None, None)
        
        # Step 4: Broadest match (ignore tags, category, and tone)
        if not filtered_captions:
            filtered_captions = filter_captions(captions, None, self.length, None, None)
        
        # If no captions found, raise an error
        if not filtered_captions:
            self.logger.error(f"No suitable captions found based on the given preferences. {len(captions)} captions available.")
            raise ValueError("No suitable captions found based on the given preferences.")
        
        # Rank captions by engagement or other metrics
        ranked_captions = sorted(
            filtered_captions,
            key=lambda c: (c.get('likes', 0) + c.get('shares', 0) + c.get('comments', 0)),
            reverse=True
        )
        
        # Select the top-ranked caption
        selected_caption = ranked_captions[0] if ranked_captions else None
        
        if not selected_caption:
            self.logger.error("No suitable captions found after filtering and ranking.")
            raise ValueError("No suitable captions found after filtering and ranking.")
        
        self.logger.info(f"Selected caption text: {selected_caption.get('caption_text')}")
        return selected_caption




    def update_user_preferences(self):
        """
        Update the user's preferences in the database.
        """
        try:
            self.db_client.update_user_preferences(self.user_id, self.preferences)
            self.logger.info(f"Preferences updated for user_id {self.user_id}")
        except Exception as e:
            self.logger.error(f"Failed to update preferences: {e}")

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
            self.db_client.update_user_preferences(self.user_id, validated_preferences)
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
            "tags": [],
            "length": "short",
            "category": "general",
            "audience": "general",
            "language": "en",
            "tone": "reserved"
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

        # Validate post preferences
        preferences["tags"] = preferences.get("tags", [])
        preferences["length"] = preferences.get("length", "short")
        preferences["category"] = preferences.get("category", "general")
        preferences["audience"] = preferences.get("audience", "general")
        preferences["language"] = preferences.get("language", "en")
        preferences["tone"] = preferences.get("tone", "reserved")

        return preferences
