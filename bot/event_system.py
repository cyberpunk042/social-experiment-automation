# bot/event_system.py
class Event:
    def __init__(self, data):
        self.data = data

class EventListener:
    def notify(self, event):
        raise NotImplementedError("Subclasses should implement this!")

class NewPostEvent(Event):
    pass

class NewPostListener(EventListener):
    def notify(self, event):
        # Logic to handle a new post event
        print(f"New post detected: {event.data}")

class EventManager:
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event_type, listener):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(listener)

    def notify(self, event_type, event):
        for listener in self.listeners.get(event_type, []):
            listener.notify(event)

# Usage
event_manager = EventManager()
new_post_listener = NewPostListener()
event_manager.subscribe(NewPostEvent, new_post_listener)

# When a new post is detected
new_post_event = NewPostEvent(data=post_data)
event_manager.notify(NewPostEvent, new_post_event)
