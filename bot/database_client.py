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
        if hasattr(self, '_initialized') and self._initialized:
            return
        self.logger = logging.getLogger(__name__)
        self.supabase_url = config_manager.get("supabase_url")
        self.supabase_key = config_manager.get("supabase_key")

        try:
            self.client = supabase.create_client(self.supabase_url, self.supabase_key)
            self.logger.info("Supabase client initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize Supabase client: {e}")
            raise

        self._initialized = True

    def get_user_preferences(self, user_id):
        try:
            response = self.client.from_("user_preferences").select("*").eq("user_id", user_id).execute()
            if response.status_code == 200 and response.data:
                self.logger.info(f"User preferences retrieved for user_id: {user_id}")
                return response.data
            else:
                self.logger.warning(f"No user preferences found for user_id: {user_id}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to retrieve user preferences for user_id: {user_id} - {e}")
            return None

    def update_user_preferences(self, user_id, preferences):
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
