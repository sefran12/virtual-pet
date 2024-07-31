# src\game\game_state.py
from dataclasses import dataclass
from typing import Optional
from src.pet.pet import Pet
from ..narration.scenario import Scenario

@dataclass
class GameState:
    pet: Pet
    current_scenario: Scenario
    previous_scenario: Optional[Scenario]
    last_interaction: Optional[str]
    last_pet_response: Optional[str]
    current_chapter_index: int