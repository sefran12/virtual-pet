# src\game\game.py
from typing import List, Dict, Optional, Union
from src.pet.pet import Pet
from ..narration.scenario import Scenario, generate_dynamic_scenario
from ..core.interfaces import GameEvent
from .choices import ScenarioChoice, FreeformChoice
from src.utils.formatters import format_pet_state, format_pet_memories
from ..narration.chapter import Chapter
from .game_state import GameState
from src.pet.updaters import update_pet_physical_description


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
            current_chapter_index=self.current_chapter_index,
        )

    def process_message(self, message: str) -> dict:
        if message == "state":
            return {
                "special_action": "show_state",
                "content": format_pet_state(self.pet),
            }
        elif message == "memories":
            return {
                "special_action": "show_memories",
                "content": format_pet_memories(self.pet),
            }
        elif message.isdigit():
            choice_index = int(message) - 1
            if 0 <= choice_index < len(self.current_scenario.choices):
                choice = self.current_scenario.choices[choice_index]
                return self.execute_choice(
                    choice, "", self.current_scenario.description
                )
            elif choice_index == len(self.current_scenario.choices):
                return self.execute_choice(
                    FreeformChoice(), "", self.current_scenario.description
                )
        return self.execute_choice(
            FreeformChoice(), message, self.current_scenario.description
        )

    def execute_choice(
        self, choice: Union[ScenarioChoice, FreeformChoice], message: str, scenario: str
    ) -> dict:
        choice.execute(self, message, scenario)
        self.generate_next_scenario()
        self.update_chapter()
        return {
            "scenario": self.current_scenario.description,
            "choices": [choice.text for choice in self.current_scenario.choices],
            "pet_state": format_pet_state(self.pet),
            "pet_response": self.last_pet_response,
        }

    def update_pet(self, interaction: str, scenario: str):
        from ..core.event_system import bus
        from ..core.state_manager import StateManager
        
        # Create state manager and take snapshot before changes
        state_manager = StateManager()
        initial_snapshot = state_manager.snapshot(self.pet)
        
        try:
            # Get state delta without applying
            delta = self.pet.process_interaction(interaction, scenario)
            
            # Validate delta structure
            required_keys = {'emotional', 'physical', 'memory'}
            if not all(key in delta for key in required_keys):
                raise ValueError(f"Invalid delta structure. Required keys: {required_keys}")
            
            # Apply validated changes
            self.pet.apply_state(delta)
            
            # Get pet's response through the response processor
            from src.pet.updaters import process_interaction_for_pet_response
            
            # Record interaction details
            self.last_interaction = interaction
            self.last_pet_response = process_interaction_for_pet_response(
                interaction,
                self.pet.emotional_state,
                self.pet.physical_state,
                delta['emotional'],
                delta['physical'],
                delta['memory'] if delta['memory'] else None,
                self.pet.physical_state.description
            )
            
            # Update chapter narrative
            current_chapter = self.chapters[self.current_chapter_index]
            current_chapter.add_to_narrative(
                self.current_scenario.description, interaction, self.last_pet_response
            )
            
            # Take final snapshot and emit game event
            final_snapshot = state_manager.snapshot(self.pet)
            bus.publish(GameEvent.INTERACTION_COMPLETED, {
                'interaction': interaction,
                'scenario': scenario,
                'initial_state': initial_snapshot,
                'final_state': final_snapshot
            })
            
            # Increment pet age (only if interaction was successful)
            self.pet.age += 0.1
            
        except Exception as e:
            # On error, restore initial state and re-raise
            self.pet = state_manager.restore(initial_snapshot)
            raise RuntimeError(f"Failed to update pet state: {str(e)}")

    def process_freeform_action(self, action: str, scenario: str):
        self.update_pet(action, scenario)

    def generate_next_scenario(self):
        self.previous_scenario = self.current_scenario
        current_chapter = self.chapters[self.current_chapter_index]
        self.current_scenario = generate_dynamic_scenario(
            self.pet,
            self.previous_scenario,
            self.last_interaction,
            self.last_pet_response,
            current_chapter,
        )

    def update_chapter(self):
        current_chapter = self.chapters[self.current_chapter_index]
        game_state = self.get_game_state()
        triggered_events = current_chapter.update(game_state)

        if current_chapter.is_completed():
            self.evolve_pet()
            self.current_chapter_index += 1
            if self.current_chapter_index < len(self.chapters):
                print(
                    f"Starting new chapter: {self.chapters[self.current_chapter_index].title}"
                )
            else:
                print("Game completed!")

    def evolve_pet(self):
        current_chapter = self.chapters[self.current_chapter_index]
        self.pet.age += current_chapter.age_increment
        new_description = update_pet_physical_description(
            self.pet, current_chapter.narrative_summary
        )
        self.pet.physical_state.description = new_description
