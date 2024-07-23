# src/game/chapter.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable

@dataclass
class ChapterEvent:
    description: str
    trigger_condition: Callable[['GameState'], bool]
    action: Callable[['GameState'], None]

@dataclass
class Chapter:
    id: str
    title: str
    description: str
    events: List[ChapterEvent]
    age_increment: int
    completed_events: List[str] = field(default_factory=list)
    narrative_summary: List[Dict[str, str]] = field(default_factory=list)

    def add_to_narrative(self, scenario: str, interaction: str, pet_response: str):
        self.narrative_summary.append({
            "scenario": scenario,
            "interaction": interaction,
            "pet_response": pet_response
        })

    def update(self, game_state: 'GameState') -> List[ChapterEvent]:
        triggered_events = []
        for event in self.events:
            if event.description not in self.completed_events and event.trigger_condition(game_state):
                event.action(game_state)
                self.completed_events.append(event.description)
                triggered_events.append(event)
        return triggered_events

    def is_completed(self) -> bool:
        return len(self.completed_events) == len(self.events)
