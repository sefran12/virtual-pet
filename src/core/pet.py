# src\core\pet.py
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

@dataclass
class Pet:
    emotional_state: EmotionalState
    physical_state: PhysicalState
    long_term_memory: LongTermMemory
    short_term_memory: ShortTermMemory
    name: str
    age: int

    def update_physical_description(self):
        # This method can be called to update the physical description based on the pet's current state
        # Implementation will depend on how you want to handle physical changes
        pass

    def process_interaction(self, interaction: str) -> str:
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
            initial_emotional_state,
            initial_physical_state,
            emotional_delta,
            physical_delta
        )

        # Generate pet's response
        response = process_interaction_for_pet_response(
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

        # Update physical description
        self.update_physical_description()

        return response

    def summarize_state(self) -> str:
        return f"""
        Name: {self.name}
        Age: {self.age}
        Physical Description: {self.physical_state.description}
        Emotional State: {self.emotional_state}
        Physical State: {self.physical_state.variables}
        Recent Memory: {self.short_term_memory.events[-1] if self.short_term_memory.events else 'No recent memories'}
        """