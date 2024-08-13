# bot/database_client.py
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class DatabaseClient:
    def __init__(self, url: str, key: str):
        self.supabase: Client = create_client(url, key)

    def insert_data(self, table: str, data: dict):
        # Function to insert data into a specified table using Supabase
        try:
            response = self.supabase.table(table).insert(data).execute()
            if response.error:
                raise Exception(response.error)
            logger.info(f"Data inserted into {table} successfully.")
            return response.data
        except Exception as e:
            logger.error(f"Failed to insert data into {table}: {e}")
            return None
