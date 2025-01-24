from typing import Protocol, runtime_checkable
from dataclasses import dataclass
from enum import Enum

class PetStateEvent(Enum):
    HUNGER_CHANGED = "hunger_changed"
    MOOD_CHANGED = "mood_changed"
    MEMORY_UPDATED = "memory_updated"

class GameEvent(Enum):
    INTERACTION_COMPLETED = "interaction_completed"
    SCENARIO_TRIGGERED = "scenario_triggered"
    CHAPTER_ADVANCED = "chapter_advanced"

@runtime_checkable
class PetActor(Protocol):
    def process_interaction(self, interaction: str, scenario: str) -> dict:
        """Calculate state delta for an interaction without modifying internal state.
        Returns:
            dict: Contains emotional/physical deltas, memory entry, and snapshot
        """
        """Returns state delta without modifying internal state"""
    
    def apply_state(self, delta: dict):
        """Applies validated state changes"""
        
    def get_snapshot(self) -> dict:
        """Returns serializable state snapshot"""

@runtime_checkable
class NarrativeSource(Protocol):
    def generate_prompt(self, state_snapshot: dict) -> str:
        """Creates narrative context from game state"""
        
    def handle_response(self, response: str) -> dict:
        """Processes narrative response into game events"""

@runtime_checkable 
class GameActions(Protocol):
    def register_actor(self, actor: PetActor):
        """Adds a new actor to the game ecosystem"""
