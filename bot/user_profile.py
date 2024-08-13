# bot/user_profile.py
import logging
from database_client import DatabaseClient

logger = logging.getLogger(__name__)

class UserProfile:
    def __init__(self, db_client: DatabaseClient):
        self.db_client = db_client

    def create_profile(self, user_id: str, profile_data: dict):
        # Function to create a new user profile
        try:
            response = self.db_client.insert_data('profiles', profile_data)
            if response:
                logger.info(f"User profile for {user_id} created successfully.")
            else:
                logger.error(f"Failed to create user profile for {user_id}.")
        except Exception as e:
            logger.error(f"Exception creating user profile for {user_id}: {e}")
