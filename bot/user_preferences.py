# bot/user_preferences.py

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
        if hasattr(self, '_initialized') and self._initialized:
            return
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        self.db_client = DatabaseClient(config_manager)
        self.preferences = {}
        self._initialized = True

    def load_preferences(self, user_id):
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
        if user_id not in self.preferences:
            self.load_preferences(user_id)
        return self.preferences.get(user_id, self._default_preferences())

    def update_preferences(self, user_id, new_preferences):
        try:
            self.db_client.update_user_preferences(user_id, new_preferences)
            self.preferences[user_id] = new_preferences
            self.logger.info(f"Updated preferences for user {user_id}")
        except Exception as e:
            self.logger.error(f"Failed to update preferences for user {user_id}: {e}")

    def _default_preferences(self):
        return {
            'tone': 'friendly',
            'style': 'casual'
        }
