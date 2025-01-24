# src\pet\pet.py
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
from src.utils.config import AIConfig

@dataclass
class Pet:
    emotional_state: EmotionalState
    physical_state: PhysicalState
    long_term_memory: LongTermMemory
    short_term_memory: ShortTermMemory
    name: str
    age: int
    species: str

    def process_interaction(self, interaction: str, scenario: str, ai_config: AIConfig) -> str:
        # Store initial states
        initial_emotional_state = self.emotional_state
        initial_physical_state = self.physical_state

        # Process emotional changes
        emotional_delta = process_interaction_to_emotional_delta(interaction, ai_config)
        new_emotional_state = apply_emotional_delta(self.emotional_state, emotional_delta)

        # Process physical changes
        physical_delta = process_interaction_to_physical_delta(interaction, ai_config)
        new_physical_state = apply_physical_delta(self.physical_state, physical_delta)

        # Generate memory
        memory = process_interaction_as_pet_memory(
            interaction,
            scenario,
            initial_emotional_state,
            initial_physical_state,
            emotional_delta,
            physical_delta,
            ai_config
        )

        # Generate pet's response
        response = process_interaction_for_pet_response(
            interaction,
            initial_emotional_state,
            initial_physical_state,
            emotional_delta,
            physical_delta,
            self.short_term_memory.events[-1] if self.short_term_memory.events else None,
            self.physical_state.description,
            ai_config
        )

        # Update pet state
        self.emotional_state = new_emotional_state
        self.physical_state = new_physical_state
        self.short_term_memory.events.append(memory)
        return response

    def summarize_state(self) -> str:
        return f"""
        Nome: {self.name}\n
        Età: {self.age}\n
        Specie: {self.species}\n
        Descrizione fisica: {self.physical_state.description}\n
        Stato emotivo: {self.emotional_state}\n
        Stato fisico: {self.physical_state.variables}\n
        Ricordo recente: {self.short_term_memory.events[-1] if self.short_term_memory.events else 'Nessun ricordo recente'}\n
        """
