# bot/database_client.py
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class DatabaseClient:
    def __init__(self, url: str, key: str):
        self.supabase: Client = create_client(url, key)

    def fetch_data(self, table: str, conditions: dict = None):
        try:
            query = self.supabase.table(table).select("*")
            if conditions:
                for key, value in conditions.items():
                    query = query.eq(key, value)
            response = query.execute()
            if response.error:
                raise Exception(response.error)
            logger.info(f"Data fetched from {table} successfully.")
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch data from {table}: {e}")
            return None

    def update_data(self, table: str, conditions: dict, updates: dict):
        try:
            query = self.supabase.table(table)
            for key, value in conditions.items():
                query = query.eq(key, value)
            response = query.update(updates).execute()
            if response.error:
                raise Exception(response.error)
            logger.info(f"Data updated in {table} successfully.")
            return response.data
        except Exception as e:
            logger.error(f"Failed to update data in {table}: {e}")
            return None

    def delete_data(self, table: str, conditions: dict):
        try:
            query = self.supabase.table(table)
            for key, value in conditions.items():
                query = query.eq(key, value)
            response = query.delete().execute()
            if response.error:
                raise Exception(response.error)
            logger.info(f"Data deleted from {table} successfully.")
            return response.data
        except Exception as e:
            logger.error(f"Failed to delete data from {table}: {e}")
            return None

