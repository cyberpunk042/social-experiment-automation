import asyncio
import logging
from queue import Queue
from datetime import datetime, timedelta

class EventSystem:
    def __init__(self):
        """
        Initialize the EventSystem class.
        
        This constructor sets up the event subscribers dictionary and the event queue
        for managing and processing events asynchronously.
        """
        self.subscribers = {}
        self.event_queue = Queue()
        self.logger = logging.getLogger(__name__)

    def subscribe(self, event_type, subscriber, priority=0):
        """
        Add a subscriber for a specific event type.
        
        :param event_type: The type of event to subscribe to.
        :param subscriber: The subscriber object that will handle the event.
        :param priority: The priority of the subscriber; higher values are processed first.
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append((priority, subscriber))
        self.subscribers[event_type].sort(reverse=True, key=lambda x: x[0])
        self.logger.info(f"Subscriber added for event type '{event_type}' with priority {priority}.")

    def notify(self, event_type, data, delay_seconds=0):
        """
        Notify the event system of a new event, optionally with a delay.
        
        :param event_type: The type of event being notified.
        :param data: The data associated with the event.
        :param delay_seconds: The delay before processing the event, in seconds.
        """
        event_time = datetime.now() + timedelta(seconds=delay_seconds)
        self.event_queue.put((event_time, event_type, data))
        self.logger.info(f"Event '{event_type}' notified with delay of {delay_seconds} seconds.")

    def should_process_event(self, event_type, data):
        """
        Determine if the event should be processed based on custom logic.
        
        :param event_type: The type of event.
        :param data: The data associated with the event.
        :return: True if the event should be processed, False otherwise.
        """
        engagement_level = data.get('engagement_level', 'medium')
        should_process = engagement_level in ['high', 'medium']
        self.logger.info(f"Event '{event_type}' processing decision: {'Proceed' if should_process else 'Skip'}")
        return should_process

    async def process_events(self):
        """
        Process events asynchronously.
        
        This method processes events from the event queue, dispatching them to
        subscribers if they are eligible for processing.
        """
        while not self.event_queue.empty():
            event_time, event_type, data = self.event_queue.get()

            # Wait until the event's scheduled time
            await asyncio.sleep(max(0, (event_time - datetime.now()).total_seconds()))

            if self.should_process_event(event_type, data):
                await self._dispatch_event(event_type, data)

    async def _dispatch_event(self, event_type, data):
        """
        Dispatch the event to all relevant subscribers.
        
        :param event_type: The type of event to dispatch.
        :param data: The data associated with the event.
        """
        if event_type in self.subscribers:
            for _, subscriber in self.subscribers[event_type]:
                try:
                    await subscriber.handle_event(event_type, data)
                    self.logger.info(f"Event '{event_type}' handled by {subscriber.__class__.__name__}.")
                except Exception as e:
                    self.logger.error(f"Error handling event '{event_type}' by {subscriber.__class__.__name__}: {e}")

    def log_event_processing(self, event_type, start_time, end_time, data):
        """
        Log the processing time of an event.
        
        :param event_type: The type of event that was processed.
        :param start_time: The time when event processing started.
        :param end_time: The time when event processing ended.
        :param data: The data associated with the event.
        """
        duration = (end_time - start_time).total_seconds()
        self.logger.info(f"Event '{event_type}' processed in {duration:.2f} seconds with data: {data}")

class BotEventSubscriber:
    def __init__(self, bot):
        """
        Initialize the BotEventSubscriber with a bot instance.
        
        :param bot: The bot instance that will handle events.
        """
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    def update(self, event_type, data):
        """
        Handle the event based on its type.
        
        :param event_type: The type of event being handled.
        :param data: The data associated with the event.
        """
        try:
            if event_type == 'NEW_POST':
                self.bot.run(data['hashtag'], data.get('context'))
            else:
                self.logger.warning(f"Unhandled event type '{event_type}'.")
        except Exception as e:
            self.logger.error(f"Error in BotEventSubscriber update method for event '{event_type}': {e}")
