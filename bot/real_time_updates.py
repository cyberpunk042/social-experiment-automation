# bot/real_time_updates.py
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class RealTimeUpdates:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)

    def subscribe_to_inserts(self, table: str, callback):
        # Function to subscribe to insert events on a table using Supabase
        try:
            subscription = self.supabase.table(table).on('INSERT', callback).subscribe()
            logger.info(f"Subscribed to insert events on {table}.")
            return subscription
        except Exception as e:
            logger.error(f"Failed to subscribe to insert events on {table}: {e}")
            return None
        
    def subscribe_to_changes(self, table: str, callback):
        # Function to subscribe to real-time updates on a table using Supabase
        try:
            subscription = self.supabase.table(table).on('*', callback).subscribe()
            logger.info(f"Subscribed to real-time updates on {table}.")
            return subscription
        except Exception as e:
            logger.error(f"Failed to subscribe to real-time updates on {table}: {e}")
            return None
