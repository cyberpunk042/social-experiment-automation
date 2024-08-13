import asyncio
import logging
from queue import Queue
from datetime import datetime, timedelta

## Example usage of the EventSystem with asyncio
## (This part would typically go in a different part of the application)
#async def example_usage(event_system):
#    # Simulate adding an event
#    event_system.notify("user_signup", {"user_id": 123, "engagement_level": "high"}, delay_seconds=2)
#    
#    # Process events asynchronously
#    await event_system.process_events()
#
## To run the example usage (outside of the class definition):
## asyncio.run(example_usage(event_system))


class EventSystem:
    def __init__(self):
        self.subscribers = {}
        self.event_queue = Queue()
        self.logger = logging.getLogger(__name__)

    def subscribe(self, event_type, subscriber, priority=0):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append((priority, subscriber))
        self.subscribers[event_type].sort(reverse=True, key=lambda x: x[0])
        self.logger.info(f"Subscriber added for event type '{event_type}' with priority {priority}.")

    def notify(self, event_type, data, delay_seconds=0):
        event_time = datetime.now() + timedelta(seconds=delay_seconds)
        self.event_queue.put((event_time, event_type, data))
        self.logger.info(f"Event '{event_type}' notified with delay of {delay_seconds} seconds.")

    def should_process_event(self, event_type, data):
        """Determine if the event should be processed based on custom logic."""
        engagement_level = data.get('engagement_level', 'medium')
        should_process = engagement_level in ['high', 'medium']
        self.logger.info(f"Event '{event_type}' processing decision: {'Proceed' if should_process else 'Skip'}")
        return should_process

    async def process_events(self):
        """Process events asynchronously."""
        while not self.event_queue.empty():
            event_time, event_type, data = self.event_queue.get()

            # Wait until the event's scheduled time
            await asyncio.sleep((event_time - datetime.now()).total_seconds())

            if self.should_process_event(event_type, data):
                await self._dispatch_event(event_type, data)

    async def _dispatch_event(self, event_type, data):
        """Dispatch the event to all relevant subscribers."""
        if event_type in self.subscribers:
            for _, subscriber in self.subscribers[event_type]:
                try:
                    await subscriber.handle_event(event_type, data)
                    self.logger.info(f"Event '{event_type}' handled by {subscriber.__class__.__name__}.")
                except Exception as e:
                    self.logger.error(f"Error handling event '{event_type}' by {subscriber.__class__.__name__}: {e}")

    def log_event_processing(self, event_type, start_time, end_time, data):
        duration = (end_time - start_time).total_seconds()
        self.logger.info(f"Event '{event_type}' processed in {duration:.2f} seconds with data: {data}")

class BotEventSubscriber:
    def __init__(self, bot):
        self.bot = bot

    def update(self, event_type, data):
        try:
            if event_type == 'NEW_POST':
                self.bot.run(data['hashtag'], data.get('context'))
            else:
                self.logger.warning(f"Unhandled event type '{event_type}'.")
        except Exception as e:
            self.logger.error(f"Error in BotEventSubscriber update method for event '{event_type}': {e}")
