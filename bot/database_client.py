import logging
import threading
from supabase import create_client, Client
from postgrest.exceptions import APIError
from config_manager import ConfigManager
from datetime import datetime, timedelta

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
        
        
    def add_generated_caption(self, caption_text, prompt, image_url, caption_id, model="gpt-3.5-turbo"):
        """
        Save an AI-generated caption to Supabase and link it to the existing caption record.

        :param caption_text: The generated caption text.
        :param prompt: The prompt used to generate the caption.
        :param caption_id: The ID of the existing caption in the captions table.
        :param model: The AI model used for generating the caption.
        :return: The inserted generated caption data.
        """
        generated_caption_data = {
            "caption_text": caption_text,
            "prompt": prompt,
            "caption_id": caption_id,  # Linking to the original caption
            "is_generated": True,
            "generation_date": datetime.now().isoformat(),
            "ai_model_used": model,
            "image_url": image_url
        }

        try:
            response = self.client.table('generated_captions').insert(generated_caption_data).execute()
            if response.data:
                self.logger.info("Generated caption saved to Supabase successfully.")
                return response.data
            else:
                self.logger.error("Failed to insert generated caption.")
                return None
        
        except APIError as api_err:
            self.logger.error(f"Supabase API Error: {api_err}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise
        
    def check_and_populate_captions(self):
        """
        Check if captions exist in the database and populate them if necessary.
        """
        captions = self.client.from_("captions").select("*").limit(1).execute()
        if not captions.data:
            self.logger.info("No captions found in the database. Populating default captions.")
            # Populate with some default captions
            default_captions = [
                {
                    "text": "The future belongs to those who believe in the beauty of their dreams.",
                    "tags": ["motivation", "inspiration"],
                    "length": "short",
                    "category": "motivational",
                    "tone": "positive",
                    "likes": 10, 
                    "shares": 2, 
                    "comments": 1
                },
                # Add more captions as necessary
            ]
            self.client.from_("captions").insert(default_captions).execute()

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
        """
        Retrieve data from a specific table in Supabase with optional filters.

        :param table_name: The name of the table to retrieve data from.
        :param filters: A dictionary of filters to apply to the query. If None, all data is retrieved.
        :return: A list of rows (each row is a dictionary) from the specified table.
        """
        try:
            query = self.client.from_(table_name).select("*")
            if filters:
                for column, value in filters.items():
                    query = query.eq(column, value)
            response = query.execute()
            
            if response.data:
                self.logger.info(f"Data retrieved from {table_name} with filters {filters}")
                return response.data
            else:
                self.logger.warning(f"No data found in table '{table_name}'.")
                return []

        except APIError as e:
            self.logger.error(f"Error retrieving data from table '{table_name}': {e}")
            return []

    def add_data(self, table_name, data):
        """
        Insert data into a specified table.

        :param table_name: The name of the table to insert data into.
        :param data: A dictionary of data to insert.
        :return: The inserted data with any generated fields (e.g., ID) or an empty list if the insert fails.
        """
        try:
            response = self.client.from_(table_name).insert(data).execute()

            if response.data:
                self.logger.info(f"Data inserted successfully into '{table_name}'.")
                return response.data
            else:
                self.logger.error(f"Failed to insert data into '{table_name}'.")
                return []

        except APIError as e:
            self.logger.error(f"Error inserting data into '{table_name}': {e}")
            return []
        
    def update_data(self, table_name, data):
        """Update data in a specific table in Supabase."""
        try:
            response = self.client.from_(table_name).upsert(data).execute()
            if response.data:
                self.logger.info(f"Data in {table_name} updated successfully")
            else:
                self.logger.error(f"Failed to update data in {table_name}: {response}")
        except Exception as e:
            self.logger.error(f"Failed to update data in {table_name}: {e}")