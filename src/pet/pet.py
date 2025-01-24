# src\pet\pet.py
from dataclasses import dataclass
from .states import EmotionalState, PhysicalState
from .memory import LongTermMemory, ShortTermMemory
from ..core.interfaces import PetStateEvent
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
    species: str

    def process_interaction(self, interaction: str, scenario: str) -> dict:
        """Returns state delta without modifying internal state (implements PetActor protocol)"""
        from ..core.event_system import bus
        from ..core.state_manager import StateManager

        # Create state manager and take snapshot
        state_mgr = StateManager()
        snapshot = state_mgr.snapshot(self)  # Pass the entire pet object for proper state capture

        # Calculate potential changes
        emotional_delta = process_interaction_to_emotional_delta(interaction)
        physical_delta = process_interaction_to_physical_delta(interaction)
        memory = process_interaction_as_pet_memory(
            interaction, scenario, self.emotional_state, 
            self.physical_state, emotional_delta, physical_delta
        )

        # Emit events for state transitions with proper variable access
        # Emit events for state transitions
        emotional_values = {var.name: var.value for var in self.emotional_state.variables}
        bus.publish(PetStateEvent.MOOD_CHANGED, {
            'old': emotional_values,
            'new': emotional_delta,
            'interaction': interaction
        })
        
        # Find hunger variable in the list and emit hunger change event
        hunger_var = next((var for var in self.physical_state.variables if var.name == 'hunger'), None)
        if hunger_var:
            bus.publish(PetStateEvent.HUNGER_CHANGED, {
                'old': hunger_var.value,
                'delta': physical_delta.get('hunger', 0),
                'source': interaction
            })

        # Return delta without applying changes
        return {
            'emotional': emotional_delta,  # Already a dict from process_interaction_to_emotional_delta
            'physical': physical_delta,    # Already a dict from process_interaction_to_physical_delta
            'memory': {'content': memory.content, 'importance': memory.importance},
            '_snapshot': snapshot
        }

    def apply_state(self, delta: dict):
        """Apply validated state changes (implements PetActor protocol)"""
        self.emotional_state = apply_emotional_delta(self.emotional_state, delta['emotional'])
        self.physical_state = apply_physical_delta(self.physical_state, delta['physical'])
        self.short_term_memory.events.append(delta['memory'])

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

    def get_snapshot(self) -> dict:
        """Returns serializable state snapshot (implements PetActor protocol)"""
        from dataclasses import asdict
        return {
            'name': self.name,
            'age': self.age,
            'species': self.species,
            'emotional_state': {
                'variables': [asdict(var) for var in self.emotional_state.variables]
            },
            'physical_state': {
                'variables': [asdict(var) for var in self.physical_state.variables],
                'description': asdict(self.physical_state.description)
            },
            'short_term_memory': [asdict(m) for m in self.short_term_memory.events],
            'long_term_memory': {
                'people': {k: asdict(v) for k, v in self.long_term_memory.people.items()},
                'events': {k: asdict(v) for k, v in self.long_term_memory.events.items()},
                'places': {k: asdict(v) for k, v in self.long_term_memory.places.items()}
            }
        }
