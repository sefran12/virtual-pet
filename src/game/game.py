
# src/game/game.py
from typing import List, Dict, Optional, Union
from src.core.pet import Pet
from .scenario import Scenario, generate_dynamic_scenario
from .choices import ScenarioChoice, FreeformChoice
from src.utils.formatters import format_pet_state, format_pet_memories

class Game:
    def __init__(self, pet: Pet, initial_scenario: Scenario):
        self.pet = pet
        self.current_scenario = initial_scenario
        self.previous_scenario: Optional[Scenario] = None
        self.last_interaction: Optional[str] = None
        self.last_pet_response: Optional[str] = None

    def process_message(self, message: str) -> dict:
        if message == "state":
            return {"special_action": "show_state", "content": format_pet_state(self.pet)}
        elif message == "memories":
            return {"special_action": "show_memories", "content": format_pet_memories(self.pet)}
        elif message.isdigit():
            choice_index = int(message) - 1
            if 0 <= choice_index < len(self.current_scenario.choices):
                choice = self.current_scenario.choices[choice_index]
                return self.execute_choice(choice, "")
            elif choice_index == len(self.current_scenario.choices):
                return self.execute_choice(FreeformChoice(), "")
        return self.execute_choice(FreeformChoice(), message)

    def execute_choice(self, choice: Union[ScenarioChoice, FreeformChoice], message: str) -> dict:
        choice.execute(self, message)
        self.generate_next_scenario()
        return {
            "scenario": self.current_scenario.description,
            "choices": [choice.text for choice in self.current_scenario.choices],
            "pet_state": format_pet_state(self.pet),
            "pet_response": self.last_pet_response
        }

    def update_pet(self, interaction: str):
        self.last_interaction = interaction
        self.last_pet_response = self.pet.process_interaction(interaction)

    def process_freeform_action(self, action: str):
        self.update_pet(action)

    def generate_next_scenario(self):
        self.previous_scenario = self.current_scenario
        self.current_scenario = generate_dynamic_scenario(
            self.pet,
            self.previous_scenario,
            self.last_interaction,
            self.last_pet_response
        )
