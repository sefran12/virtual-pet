import unittest
from dataclasses import asdict
from src.game.game_state import GameState
from src.pet.pet import Pet
from src.narration.scenario import Scenario
from src.pet.states import EmotionalState, PhysicalState, LatentVariable, PhysicalDescription
from src.pet.memory import LongTermMemory, ShortTermMemory
from src.core.interfaces import GameEvent
from src.core.event_system import bus

def create_test_pet():
    """Create a test pet with standard initial state"""
    emotional_vars = [
        LatentVariable("happiness", 50),
        LatentVariable("excitement", 50),
        LatentVariable("calmness", 50),
        LatentVariable("curiosity", 50),
        LatentVariable("affection", 50)
    ]
    physical_vars = [
        LatentVariable("hunger", 50),
        LatentVariable("tiredness", 50),
        LatentVariable("health", 50),
        LatentVariable("cleanliness", 50)
    ]
    description = PhysicalDescription(
        species="test species",
        color="test color",
        size="medium",
        distinctive_features=["test feature"]
    )
    return Pet(
        emotional_state=EmotionalState(variables=emotional_vars),
        physical_state=PhysicalState(variables=physical_vars, description=description),
        long_term_memory=LongTermMemory(),
        short_term_memory=ShortTermMemory(),
        name="TestPet",
        age=1,
        species="test species"
    )

def create_test_scenario():
    """Create a test scenario"""
    return Scenario(
        id="test_scenario",
        description="Test scenario",
        choices=[]
    )

class TestGameStateInterface(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.pet = create_test_pet()
        self.scenario = create_test_scenario()
        self.state = GameState(
            pet=self.pet,
            current_scenario=self.scenario,
            previous_scenario=None,
            last_interaction=None,
            last_pet_response=None,
            current_chapter_index=0
        )
        bus.clear_subscriptions()

    def test_state_immutability(self):
        """Verify GameState maintains immutability of core state"""
        # Capture initial state
        initial_snapshot = self.pet.get_snapshot()
        
        # Simulate interaction
        self.state.last_interaction = "test interaction"
        self.state.last_pet_response = "test response"
        
        # Verify pet state hasn't changed
        current_snapshot = self.pet.get_snapshot()
        self.assertEqual(initial_snapshot, current_snapshot,
                        "Pet state should not change from GameState updates")

    def test_event_emission(self):
        """Verify GameState properly emits events"""
        events_received = []
        
        def event_handler(data):
            events_received.append(data)
            
        bus.subscribe(GameEvent.INTERACTION_COMPLETED, event_handler)
        
        # Simulate interaction
        delta = self.pet.process_interaction("test", "test scenario")
        self.pet.apply_state(delta)
        
        # Verify event was emitted
        self.assertEqual(len(events_received), 1)
        self.assertIn('interaction', events_received[0])
        self.assertIn('scenario', events_received[0])
        self.assertIn('snapshot', events_received[0])

if __name__ == '__main__':
    unittest.main()
