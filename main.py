from src.core.pet import Pet
from src.core.states import EmotionalState, PhysicalState, PhysicalDescription, LatentVariable
from src.core.memory import LongTermMemory, ShortTermMemory
from src.game.game import Game
from src.game.scenario import generate_dynamic_scenario


def create_initial_pet():
    emotional_state = EmotionalState([
        LatentVariable("happiness", 50),
        LatentVariable("excitement", 50),
        LatentVariable("calmness", 50),
        LatentVariable("curiosity", 50),
        LatentVariable("affection", 50)
    ])
    physical_state = PhysicalState(
        variables=[
            LatentVariable("hunger", 50),
            LatentVariable("tiredness", 50),
            LatentVariable("health", 50),
            LatentVariable("cleanliness", 50)
        ],
        description=PhysicalDescription(
            species="dog",
            color="golden",
            size="medium",
            distinctive_features=["floppy ears", "wagging tail"]
        )
    )
    return Pet(
        emotional_state=emotional_state,
        physical_state=physical_state,
        long_term_memory=LongTermMemory(),
        short_term_memory=ShortTermMemory(),
        name="Buddy",
        age=3
    )

def main():
    pet = create_initial_pet()
    initial_scenario = generate_dynamic_scenario(pet, None, None, None)
    game = Game(pet, initial_scenario)

    while True:
        print(game.current_scenario.description)
        for i, choice in enumerate(game.current_scenario.choices, 1):
            print(f"{i}. {choice.text}")
        print(f"{len(game.current_scenario.choices) + 1}. [Freeform Action]")
        print("Additional options:")
        print("- Enter 'state' to see detailed pet state")
        print("- Enter 'memories' to see pet's memories")
        print("- Enter 'quit' to exit the game")

        user_input = input("Enter your choice: ")
        if user_input.lower() == 'quit':
            break

        result = game.process_message(user_input)
        
        if 'special_action' in result:
            print(result['content'])
        else:
            print(f"Pet's response: {result['pet_response']}")
            print(result["pet_state"])


if __name__ == "__main__":
    main()