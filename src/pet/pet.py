from dataclasses import dataclass
from .states import EmotionalState, PhysicalState
from .memory import LongTermMemory, ShortTermMemory
from .updaters import (
    process_interaction_to_emotional_delta,
    process_interaction_to_physical_delta,
    apply_emotional_delta,
    apply_physical_delta,
    process_interaction_as_pet_memory,
    process_interaction_for_pet_response
)
from src.utils.resource_manager import ResourceManager

resource_manager = ResourceManager()

@dataclass
class Pet:
    emotional_state: EmotionalState
    physical_state: PhysicalState
    long_term_memory: LongTermMemory
    short_term_memory: ShortTermMemory
    name: str
    age: int
    species: str
    language: str = 'english'

    def process_interaction(self, interaction: str, scenario: str) -> str:
        # Store initial states
        initial_emotional_state = self.emotional_state
        initial_physical_state = self.physical_state

        # Process emotional changes
        emotional_delta = process_interaction_to_emotional_delta(interaction)
        new_emotional_state = apply_emotional_delta(self.emotional_state, emotional_delta)

        # Process physical changes
        physical_delta = process_interaction_to_physical_delta(interaction)
        new_physical_state = apply_physical_delta(self.physical_state, physical_delta)

        # Generate memory
        memory = process_interaction_as_pet_memory(
            interaction,
            scenario,
            initial_emotional_state,
            initial_physical_state,
            emotional_delta,
            physical_delta
        )

        # Generate pet's response
        response_prompt = resource_manager.get_prompt('pet', 'process_interaction_for_pet_response', self.language)
        response = process_interaction_for_pet_response(
            response_prompt,
            interaction,
            initial_emotional_state,
            initial_physical_state,
            emotional_delta,
            physical_delta,
            self.short_term_memory.events[-1] if self.short_term_memory.events else None,
            self.physical_state.description
        )

        # Update pet state
        self.emotional_state = new_emotional_state
        self.physical_state = new_physical_state
        self.short_term_memory.events.append(memory)
        return response

    def summarize_state(self) -> str:
        summary_template = resource_manager.get_prompt('pet', 'summarize_state', self.language)
        return summary_template.format(
            name=self.name,
            age=self.age,
            species=self.species,
            physical_description=self.physical_state.description,
            emotional_state=self.emotional_state,
            physical_state=self.physical_state.variables,
            recent_memory=self.short_term_memory.events[-1] if self.short_term_memory.events else 'No recent memory'
        )