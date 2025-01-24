import unittest
from src.pet.pet import Pet
from src.pet.states import EmotionalState, PhysicalState, LatentVariable, PhysicalDescription
from src.pet.memory import LongTermMemory, ShortTermMemory
from src.core.interfaces import PetActor

class TestPetBehaviorContracts(unittest.TestCase):
    def setUp(self):
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
        self.pet = Pet(
            emotional_state=EmotionalState(variables=emotional_vars),
            physical_state=PhysicalState(variables=physical_vars, description=description),
            long_term_memory=LongTermMemory(),
            short_term_memory=ShortTermMemory(),
            name="Test Pet",
            age=1,
            species="test species"
        )

    def test_pet_actor_protocol(self):
        """Verify Pet implements PetActor protocol correctly"""
        self.assertTrue(isinstance(self.pet, PetActor))
        
        # Test process_interaction
        delta = self.pet.process_interaction("test interaction", "test scenario")
        self.assertIn('emotional', delta)
        self.assertIn('physical', delta)
        self.assertIn('memory', delta)
        self.assertIn('_snapshot', delta)
        
        # Test apply_state
        self.pet.apply_state(delta)
        
        # Test get_snapshot
        snapshot = self.pet.get_snapshot()
        self.assertIn('emotional_state', snapshot)
        self.assertIn('physical_state', snapshot)
        self.assertIn('short_term_memory', snapshot)
        self.assertIn('long_term_memory', snapshot)
    def test_state_delta_validation(self):
        """Verify state changes are properly validated"""
        # Get state delta
        delta = self.pet.process_interaction("feed", "feeding time")
        
        # Verify delta structure
        self.assertIsInstance(delta['emotional'], dict)
        self.assertIsInstance(delta['physical'], dict)
        self.assertIsInstance(delta['memory'], dict)
        
        # Verify snapshot is created
        self.assertIn('_snapshot', delta)
        self.assertIsInstance(delta['_snapshot'], dict)

    def test_state_application(self):
        """Verify state changes are properly applied"""
        # Get initial values
        initial_hunger = next(v.value for v in self.pet.physical_state.variables if v.name == "hunger")
        initial_happiness = next(v.value for v in self.pet.emotional_state.variables if v.name == "happiness")
        
        # Process interaction
        delta = self.pet.process_interaction("feed", "feeding time")
        self.pet.apply_state(delta)
        
        # Verify changes
        new_hunger = next(v.value for v in self.pet.physical_state.variables if v.name == "hunger")
        new_happiness = next(v.value for v in self.pet.emotional_state.variables if v.name == "happiness")
        
        self.assertNotEqual(initial_hunger, new_hunger, "Hunger should change after feeding")
        self.assertNotEqual(initial_happiness, new_happiness, "Happiness should change after feeding")

if __name__ == '__main__':
    unittest.main()
