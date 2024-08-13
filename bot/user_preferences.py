import logging
from bot.config_manager import ConfigManager
from bot.database_client import DatabaseClient  # Assuming this is the class managing Supabase interactions

class UserPreferences:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(UserPreferences, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize UserPreferences with access to the configuration manager and database client.
        """
        if hasattr(self, '_initialized') and self._initialized:
            return
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        self.db_client = DatabaseClient(self.config_manager)
        self.preferences = {}
        self._initialized = True

    def load_preferences(self, user_id):
        """
        Load user preferences from Supabase.
        
        :param user_id: The ID of the user whose preferences are to be loaded.
        """
        try:
            preferences = self.db_client.get_user_preferences(user_id)
            if preferences:
                self.preferences[user_id] = preferences
                self.logger.info(f"Loaded preferences for user {user_id}")
            else:
                self.logger.info(f"No preferences found for user {user_id}, using defaults.")
                self.preferences[user_id] = self._default_preferences()
        except Exception as e:
            self.logger.error(f"Failed to load preferences for user {user_id}: {e}")
            self.preferences[user_id] = self._default_preferences()

    def get_preferences(self, user_id):
        """
        Get preferences for a specific user.

        :param user_id: The ID of the user whose preferences are to be retrieved.
        :return: A dictionary of preferences for the user.
        """
        if user_id not in self.preferences:
            self.load_preferences(user_id)
        return self.preferences.get(user_id, self._default_preferences())

    def update_preferences(self, user_id, new_preferences):
        """
        Update the preferences for a specific user in Supabase.

        :param user_id: The ID of the user whose preferences are to be updated.
        :param new_preferences: A dictionary of new preferences to set for the user.
        """
        try:
            self.db_client.update_user_preferences(user_id, new_preferences)
            self.preferences[user_id] = new_preferences
            self.logger.info(f"Updated preferences for user {user_id}")
        except Exception as e:
            self.logger.error(f"Failed to update preferences for user {user_id}: {e}")

    def _default_preferences(self):
        """
        Return the default preferences for a user.
        
        :return: A dictionary of default preferences.
        """
        return {
            'tone': 'friendly',
            'style': 'casual'
        }
