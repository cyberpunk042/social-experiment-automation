# bot/event_system.p
class EventSystem:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type, subscriber, priority=0):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append((priority, subscriber))
        # Sort subscribers by priority
        self.subscribers[event_type].sort(reverse=True, key=lambda x: x[0])

    def notify(self, event_type, data):
        if event_type in self.subscribers:
            for _, subscriber in self.subscribers[event_type]:
                subscriber.update(event_type, data)

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

# Triggering events
event_system.notify('NEW_POST', {'hashtag': '#exampleHashtag', 'context': 'Positive sentiment'})
event_system.notify('TIME_TRIGGER', {'identifier': '#scheduledHashtag', 'context': 'Scheduled event context'})
