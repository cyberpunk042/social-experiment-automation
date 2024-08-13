# bot/user_preferences.py
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class UserPreferences:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)

    def get_preferences(self, user_id: str):
        # Function to retrieve user preferences using Supabase
        try:
            response = self.supabase.table('preferences').select('*').eq('user_id', user_id).execute()
            if response.error:
                raise Exception(response.error)
            logger.info(f"Preferences retrieved for user {user_id}.")
            return response.data
        except Exception as e:
            logger.error(f"Failed to retrieve preferences for user {user_id}: {e}")
            return None

    def update_preferences(self, user_id: str, preferences: dict):
        # Function to update user preferences using Supabase
        try:
            response = self.supabase.table('preferences').update(preferences).eq('user_id', user_id).execute()
            if response.error:
                raise Exception(response.error)
            logger.info(f"Preferences updated for user {user_id}.")
            return response.data
        except Exception as e:
            logger.error(f"Exception updating preferences for user {user_id}: {e}")
            return None
