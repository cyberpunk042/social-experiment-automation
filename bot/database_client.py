# bot/database_client.py

import logging
import supabase
from bot.config_manager import ConfigManager

class DatabaseClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseClient, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the DatabaseClient with Supabase configuration.
        """
        if hasattr(self, '_initialized') and self._initialized:
            return
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        self.supabase_url = self.config_manager.get("supabase", "url")
        self.supabase_key = self.config_manager.get("supabase", "key")
        self.client = supabase.create_client(self.supabase_url, self.supabase_key)
        self._initialized = True

    def get_user_preferences(self, user_id):
        """
        Retrieve user preferences from Supabase.

        :param user_id: The ID of the user whose preferences are to be retrieved.
        :return: A dictionary of user preferences if found, otherwise None.
        """
        try:
            response = self.client.from_("user_preferences").select("*").eq("user_id", user_id).execute()
            if response.status_code == 200 and response.data:
                return response.data[0]  # Assuming the first result contains the preferences
            self.logger.info(f"No preferences found for user {user_id}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to retrieve preferences for user {user_id}: {e}")
            return None

    def update_user_preferences(self, user_id, preferences):
        """
        Update user preferences in Supabase.

        :param user_id: The ID of the user whose preferences are to be updated.
        :param preferences: A dictionary of preferences to update.
        """
        try:
            response = self.client.from_("user_preferences").upsert({"user_id": user_id, **preferences}).execute()
            if response.status_code == 200:
                self.logger.info(f"Preferences for user {user_id} updated successfully")
            else:
                self.logger.error(f"Failed to update preferences for user {user_id}: {response.error_message}")
        except Exception as e:
            self.logger.error(f"Failed to update preferences for user {user_id}: {e}")

    def get_data(self, table_name, filters=None):
        """
        Retrieve data from a specific table in Supabase with optional filters.

        :param table_name: The name of the table to retrieve data from.
        :param filters: A dictionary of filters to apply to the query.
        :return: The retrieved data or None if an error occurs.
        """
        try:
            query = self.client.from_(table_name).select("*")
            if filters:
                for column, value in filters.items():
                    query = query.eq(column, value)
            response = query.execute()
            if response.status_code == 200:
                return response.data
            self.logger.error(f"Failed to retrieve data from {table_name}: {response.error_message}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to retrieve data from {table_name}: {e}")
            return None

    def update_data(self, table_name, data):
        """
        Update data in a specific table in Supabase.

        :param table_name: The name of the table to update data in.
        :param data: A dictionary of data to upsert.
        """
        try:
            response = self.client.from_(table_name).upsert(data).execute()
            if response.status_code == 200:
                self.logger.info(f"Data in {table_name} updated successfully")
            else:
                self.logger.error(f"Failed to update data in {table_name}: {response.error_message}")
        except Exception as e:
            self.logger.error(f"Failed to update data in {table_name}: {e}")
