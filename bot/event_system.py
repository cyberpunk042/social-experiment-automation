from queue import Queue
from datetime import datetime, timedelta
import logging

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
        # Custom logic to determine if the event should be processed
        # Example: only process if user engagement is high
        engagement_level = data.get('engagement_level', 'medium')
        should_process = engagement_level in ['high', 'medium']
        self.logger.info(f"Event '{event_type}' processing decision: {'Proceed' if should_process else 'Skip'}")
        return should_process

    def process_events(self):
        while not self.event_queue.empty():
            event_time, event_type, data = self.event_queue.get()
            start_time = datetime.now()

            if datetime.now() >= event_time:
                if event_type in self.subscribers:
                    for _, subscriber in self.subscribers[event_type]:
                        if self.should_process_event(event_type, data):
                            try:
                                subscriber.update(event_type, data)
                                end_time = datetime.now()
                                self.log_event_processing(event_type, start_time, end_time, data)
                            except Exception as e:
                                self.logger.error(f"Error processing event '{event_type}': {e}")
                else:
                    self.logger.warning(f"No subscribers for event type '{event_type}'.")
            else:
                # Re-queue the event if it's not yet time
                self.event_queue.put((event_time, event_type, data))
                self.logger.info(f"Event '{event_type}' re-queued for later processing.")

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
