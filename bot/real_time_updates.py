import logging
from supabase import create_client, Client
import time

logger = logging.getLogger(__name__)

class RealTimeUpdates:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.subscriptions = []

    def subscribe_to_inserts(self, table: str, callback):
        # Function to subscribe to insert events on a table using Supabase
        return self._subscribe(table, 'INSERT', callback)

    def subscribe_to_changes(self, table: str, callback):
        # Function to subscribe to real-time updates on a table using Supabase
        return self._subscribe(table, '*', callback)

    def _subscribe(self, table: str, event_type: str, callback):
        retries = 3
        delay = 2

        for attempt in range(retries):
            try:
                subscription = self.supabase.table(table).on(event_type, callback).subscribe()
                self.subscriptions.append(subscription)
                logger.info(f"Subscribed to {event_type} events on {table}.")
                return subscription
            except Exception as e:
                logger.error(f"Failed to subscribe to {event_type} events on {table} (Attempt {attempt + 1}/{retries}): {e}")
                time.sleep(delay)
                delay *= 2

        logger.error(f"Could not subscribe to {event_type} events on {table} after {retries} attempts.")
        return None

    def unsubscribe_all(self):
        for subscription in self.subscriptions:
            try:
                subscription.unsubscribe()
                logger.info("Unsubscribed from a real-time event.")
            except Exception as e:
                logger.error(f"Failed to unsubscribe: {e}")
        self.subscriptions.clear()
