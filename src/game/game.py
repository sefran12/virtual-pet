# src/game/game.py
from typing import List, Dict, Optional, Union
from src.core.pet import Pet
from .scenario import Scenario, generate_dynamic_scenario
from .choices import ScenarioChoice, FreeformChoice
from src.utils.formatters import format_pet_state, format_pet_memories
from .chapter import Chapter
from .game_state import GameState
from src.core.updaters import update_pet_physical_description

class Game:
    def __init__(self, pet: Pet, initial_scenario: Scenario, chapters: List[Chapter]):
        self.pet = pet
        self.current_scenario = initial_scenario
        self.previous_scenario: Optional[Scenario] = None
        self.last_interaction: Optional[str] = None
        self.last_pet_response: Optional[str] = None
        self.chapters = chapters
        self.current_chapter_index = 0

    def get_game_state(self) -> GameState:
        return GameState(
            pet=self.pet,
            current_scenario=self.current_scenario,
            previous_scenario=self.previous_scenario,
            last_interaction=self.last_interaction,
            last_pet_response=self.last_pet_response,
            current_chapter_index=self.current_chapter_index
        )

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
        self.update_chapter()
        return {
            "scenario": self.current_scenario.description,
            "choices": [choice.text for choice in self.current_scenario.choices],
            "pet_state": format_pet_state(self.pet),
            "pet_response": self.last_pet_response
        }

    def update_pet(self, interaction: str):
        self.last_interaction = interaction
        self.last_pet_response = self.pet.process_interaction(interaction)
        current_chapter = self.chapters[self.current_chapter_index]
        current_chapter.add_to_narrative(self.current_scenario.description, interaction, self.last_pet_response)
        # Increment pet age with each interaction
        self.pet.age += 0.1

    def process_freeform_action(self, action: str):
        self.update_pet(action)

    def generate_next_scenario(self):
        self.previous_scenario = self.current_scenario
        current_chapter = self.chapters[self.current_chapter_index]
        self.current_scenario = generate_dynamic_scenario(
            self.pet,
            self.previous_scenario,
            self.last_interaction,
            self.last_pet_response,
            current_chapter
        )

    def update_chapter(self):
        current_chapter = self.chapters[self.current_chapter_index]
        game_state = self.get_game_state()
        triggered_events = current_chapter.update(game_state)
        
        if current_chapter.is_completed():
            self.evolve_pet()
            self.current_chapter_index += 1
            if self.current_chapter_index < len(self.chapters):
                print(f"Starting new chapter: {self.chapters[self.current_chapter_index].title}")
            else:
                print("Game completed!")

    def evolve_pet(self):
        current_chapter = self.chapters[self.current_chapter_index]
        self.pet.age += current_chapter.age_increment
        new_description = update_pet_physical_description(self.pet, current_chapter.narrative_summary)
        self.pet.physical_state.description = new_description