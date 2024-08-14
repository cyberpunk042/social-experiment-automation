import logging
import threading
from supabase import create_client, Client
from postgrest.exceptions import APIError
from config_manager import ConfigManager

class DatabaseClient:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(DatabaseClient, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_manager: ConfigManager):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self.logger = logging.getLogger(__name__)
        self.supabase_url = config_manager.get("supabase_url")
        self.supabase_key = config_manager.get("supabase_key")

        try:
            self.client: Client = create_client(self.supabase_url, self.supabase_key)
            self.logger.info("Supabase client initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize Supabase client: {e}")
            raise

        self._initialized = True

    def check_table_exists(self, table_name):
        """Check if the table exists by querying it, even if it has no entries."""
        try:
            response = self.client.table(table_name).select("*").limit(1).execute()

            # Log the raw response for debugging purposes
            self.logger.debug(f"Raw response from Supabase for table '{table_name}': {response}")

            # Check if the response has data or is an empty list (which is valid if the table is empty)
            if response.data is not None:
                self.logger.info(f"Table '{table_name}' exists and is accessible.")
                return True
            else:
                self.logger.warning(f"Table '{table_name}' might exist but is empty or cannot be accessed.")
                return True  # Assume the table exists even if it has no data

        except APIError as e:
            self.logger.error(f"Error checking table existence: {e}")
            return False

    def add_caption(self, caption_data):
        self.validate_caption_schema(caption_data)

        if not self.check_table_exists('captions'):
            self.logger.error("Cannot add caption: 'captions' table does not exist.")
            raise Exception("Table not found (404).")

        try:
            self.logger.debug(f"Attempting to insert caption data: {caption_data}")

            response = self.client.table('captions').insert(caption_data).execute()

            if response.data is None:
                self.logger.error(f"Failed to insert caption data: {response}")
                raise APIError("Failed to insert caption data")

            return response.data

        except APIError as api_err:
            self.logger.error(f"Supabase API Error: {api_err}")
            try:
                self.logger.error(f"API Error response content: {api_err.args[0]}")
            except AttributeError:
                self.logger.error("API Error response content is not available.")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise
        
    def validate_caption_schema(self, caption_data):
        required_keys = {"caption_text", "tags", "length", "category", "tone"}
        if not required_keys.issubset(caption_data.keys()):
            missing_keys = required_keys - caption_data.keys()
            raise ValueError(f"Missing required keys in caption data: {missing_keys}")
        
    def get_user_preferences(self, user_id):
        try:
            response = self.client.from_("user_preferences").select("*").eq("user_id", user_id).execute()
            if response.data:
                self.logger.info(f"User preferences retrieved for user_id: {user_id}")
                return response.data
            else:
                self.logger.warning(f"No user preferences found for user_id: {user_id}")
                return None
        except Exception as e:
            self.logger.error(f"Error retrieving user preferences for user_id {user_id}: {e}")
            return None

    def update_user_preferences(self, user_id, preferences):
        try:
            response = self.client.from_("user_preferences").upsert({"user_id": user_id, **preferences}).execute()
            if response.data:
                self.logger.info(f"Preferences for user {user_id} updated successfully")
            else:
                self.logger.error(f"Failed to update preferences for user {user_id}: {response}")
        except Exception as e:
            self.logger.error(f"Failed to update preferences for user {user_id}: {e}")

    def get_data(self, table_name, filters=None):
        try:
            query = self.client.from_(table_name).select("*")
            if filters:
                for column, value in filters.items():
                    query = query.eq(column, value)
            response = query.execute()
            if response.data:
                self.logger.info(f"Data retrieved from {table_name} with filters {filters}")
                return response.data
            self.logger.error(f"Failed to retrieve data from {table_name}: {response}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to retrieve data from {table_name}: {e}")
            return None

    def update_data(self, table_name, data):
        try:
            response = self.client.from_(table_name).upsert(data).execute()
            if response.data:
                self.logger.info(f"Data in {table_name} updated successfully")
            else:
                self.logger.error(f"Failed to update data in {table_name}: {response}")
        except Exception as e:
            self.logger.error(f"Failed to update data in {table_name}: {e}")
