import logging
from supabase import create_client, Client
import time

logger = logging.getLogger(__name__)

class RealTimeUpdates:
    def __init__(self, supabase_url: str, supabase_key: str):
        """
        Initialize the RealTimeUpdates class.

        This constructor creates a Supabase client and initializes the subscription list.

        :param supabase_url: The URL of the Supabase instance.
        :param supabase_key: The API key for the Supabase instance.
        """
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.subscriptions = []

    def subscribe_to_inserts(self, table: str, callback):
        """
        Subscribe to insert events on a specific table using Supabase.

        :param table: The name of the table to subscribe to.
        :param callback: The callback function to be executed when an insert event occurs.
        :return: The subscription object if successful, None otherwise.
        """
        return self._subscribe(table, 'INSERT', callback)

    def subscribe_to_changes(self, table: str, callback):
        """
        Subscribe to real-time updates (all changes) on a specific table using Supabase.

        :param table: The name of the table to subscribe to.
        :param callback: The callback function to be executed when any event occurs.
        :return: The subscription object if successful, None otherwise.
        """
        return self._subscribe(table, '*', callback)

    def _subscribe(self, table: str, event_type: str, callback):
        """
        Handle the subscription to a specific event type on a table with retry logic.

        :param table: The name of the table to subscribe to.
        :param event_type: The type of event to subscribe to (e.g., 'INSERT', '*').
        :param callback: The callback function to be executed when the event occurs.
        :return: The subscription object if successful, None otherwise.
        """
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
        """
        Unsubscribe from all active subscriptions.

        This method attempts to unsubscribe from all real-time events and clears the subscription list.
        """
        for subscription in self.subscriptions:
            try:
                subscription.unsubscribe()
                logger.info("Unsubscribed from a real-time event.")
            except Exception as e:
                logger.error(f"Failed to unsubscribe: {e}")
        self.subscriptions.clear()
