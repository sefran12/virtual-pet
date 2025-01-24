from collections import defaultdict
from typing import Callable, Any
from .interfaces import PetStateEvent, GameEvent

class EventBus:
    def __init__(self):
        self._subscriptions = defaultdict(list)
        self._dead_letters = []

    def subscribe(self, event_type: PetStateEvent | GameEvent, handler: Callable[[Any], None]):
        self._subscriptions[event_type].append(handler)

    def publish(self, event_type: PetStateEvent | GameEvent, data: Any = None):
        if event_type not in self._subscriptions:
            self._dead_letters.append((event_type, data))
            return
            
        for handler in self._subscriptions[event_type]:
            try:
                handler(data)
            except Exception as e:
                self._dead_letters.append((event_type, data, str(e)))

    def get_dead_letters(self):
        return self._dead_letters.copy()

    def clear_subscriptions(self):
        self._subscriptions.clear()

# Singleton event bus instance
bus = EventBus()
