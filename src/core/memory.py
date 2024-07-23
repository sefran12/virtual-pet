# src\core\memory.py
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Memory:
    content: str
    importance: float

@dataclass
class ShortTermMemory:
    events: List[Memory] = field(default_factory=list)

    def add_memory(self, memory: Memory):
        self.events.append(memory)
        # Keep only the last 10 memories
        self.events = self.events[-10:]

@dataclass
class LongTermMemory:
    people: Dict[str, Memory] = field(default_factory=dict)
    events: Dict[str, Memory] = field(default_factory=dict)
    places: Dict[str, Memory] = field(default_factory=dict)

    def add_memory(self, category: str, key: str, memory: Memory):
        if category in ['people', 'events', 'places']:
            getattr(self, category)[key] = memory
        else:
            raise ValueError(f"Invalid category: {category}")