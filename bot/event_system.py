from queue import Queue

from datetime import datetime, timedelta

class EventSystem:
    def __init__(self):
        self.subscribers = {}
        self.event_queue = Queue()

    def subscribe(self, event_type, subscriber, priority=0):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append((priority, subscriber))
        self.subscribers[event_type].sort(reverse=True, key=lambda x: x[0])

    def notify(self, event_type, data, delay_seconds=0):
        event_time = datetime.now() + timedelta(seconds=delay_seconds)
        self.event_queue.put((event_time, event_type, data))
        
    def should_process_event(self, event_type, data):
        # Add logic to determine if the event should be processed
        # Example: only process if user engagement is high
        engagement_level = data.get('engagement_level', 'medium')
        return engagement_level in ['high', 'medium']
    
    def process_events(self):
        while not self.event_queue.empty():
            event_time, event_type, data = self.event_queue.get()
            start_time = datetime.now()
            if datetime.now() >= event_time:
                if event_type in self.subscribers:
                    for _, subscriber in self.subscribers[event_type]:
                        if self.should_process_event(event_type, data):
                            subscriber.update(event_type, data)
                            end_time = datetime.now()
                            self.log_event_processing(event_type, start_time, end_time, data)
            else:
                # Re-queue the event if it's not yet time
                self.event_queue.put((event_time, event_type, data))

class BotEventSubscriber:
    def __init__(self, bot):
        self.bot = bot

    def update(self, event_type, data):
        if event_type == 'NEW_POST':
            self.bot.run(data['hashtag'], data.get('context'))
        elif event_type == 'TIME_TRIGGER':
            self.bot.run(data['identifier'], data.get('context'))

# Usage
event_system = EventSystem()
bot_event_subscriber = BotEventSubscriber(bot)
event_system.subscribe('NEW_POST', bot_event_subscriber, priority=1)
event_system.subscribe('TIME_TRIGGER', bot_event_subscriber, priority=2)

# Trigger events
event_system.notify('NEW_POST', {'hashtag': '#exampleHashtag', 'context': 'Positive sentiment'}, delay_seconds=10)
event_system.notify('TIME_TRIGGER', {'identifier': '#scheduledHashtag', 'context': 'Scheduled event context'}, delay_seconds=30)
event_system.process_events()

class BotEventSubscriber:
    def __init__(self, bot):
        self.bot = bot

    def update(self, event_type, data):
        if event_type == 'NEW_POST':
            self.bot.run(data['hashtag'], data.get('context'))
        elif event_type == 'TIME_TRIGGER':
            self.bot.run(data['identifier'], data.get('context'))

# Usage
event_system = EventSystem()
bot_event_subscriber = BotEventSubscriber(bot)
event_system.subscribe('NEW_POST', bot_event_subscriber, priority=1)
event_system.subscribe('TIME_TRIGGER', bot_event_subscriber, priority=2)

# Simulating event processing loop
event_system.notify('NEW_POST', {'hashtag': '#exampleHashtag', 'context': 'Positive sentiment'})
event_system.notify('TIME_TRIGGER', {'identifier': '#scheduledHashtag', 'context': 'Scheduled event context'})
event_system.process_events()
