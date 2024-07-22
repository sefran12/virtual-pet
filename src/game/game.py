from typing import List, Dict
from src.core.pet import Pet
from src.core.updaters import process_interaction_to_emotional_delta, process_interaction_to_physical_delta, apply_emotional_delta, apply_physical_delta, process_interaction_as_pet_memory, process_interaction_for_pet_response
from .scenario import Scenario

class Game:
    def __init__(self, pet: Pet, scenarios: List[Scenario]):
        self.pet = pet
        self.scenarios: Dict[str, Scenario] = {scenario.id: scenario for scenario in scenarios}
        self.current_scenario: Scenario = scenarios[0]

    def start(self):
        while True:
            self.display_current_scenario()
            choice = self.get_user_choice()
            if choice is None:
                break
            choice.execute(self)

    def display_current_scenario(self):
        print(self.current_scenario.description)
        for i, choice in enumerate(self.current_scenario.choices, 1):
            print(f"{i}. {choice.text}")

    def get_user_choice(self) -> Scenario:
        while True:
            try:
                choice = int(input("Enter your choice (or 0 to quit): "))
                if choice == 0:
                    return None
                if 1 <= choice <= len(self.current_scenario.choices):
                    return self.current_scenario.choices[choice - 1]
                print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def change_scenario(self, scenario_id: str):
        if scenario_id in self.scenarios:
            self.current_scenario = self.scenarios[scenario_id]
        else:
            print(f"Error: Scenario '{scenario_id}' not found.")
            
    def update_pet(self, interaction: str):
        response = self.pet.process_interaction(interaction)
        print(response)
        print(self.pet.summarize_state())

    @classmethod
    def from_json(cls, pet: Pet, json_file: str, choice_actions: dict):
        scenarios = Scenario.load_scenarios(json_file, choice_actions)
        return cls(pet, scenarios)