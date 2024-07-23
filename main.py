# main.py
from src.core.pet import Pet
from src.core.states import EmotionalState, PhysicalState, PhysicalDescription, LatentVariable
from src.core.memory import LongTermMemory, ShortTermMemory
from src.game.game import Game
from src.game.scenario import generate_dynamic_scenario
from src.game.chapter import Chapter, ChapterEvent
from src.game.game_state import GameState


def create_initial_pet():
    emotional_state = EmotionalState([
        LatentVariable("curiosity", 50),
        LatentVariable("attachment", 0),
        LatentVariable("contentment", 50),
        LatentVariable("aggression", 20),
        LatentVariable("fear", 30)
    ])
    physical_state = PhysicalState(
        variables=[
            LatentVariable("energy", 100),
            LatentVariable("growth", 0),
            LatentVariable("health", 100),
            LatentVariable("magical_power", 10)
        ],
        description=PhysicalDescription(
            species="egg",
            color="silver",
            size="small",
            distinctive_features=["intricate patterns", "faint glow"]
        )
    )
    return Pet(
        emotional_state=emotional_state,
        physical_state=physical_state,
        long_term_memory=LongTermMemory(),
        short_term_memory=ShortTermMemory(),
        name="Unknown",
        age=0,
        species="egg"
    )

def create_chapters():
    return [
        Chapter(
            id="chapter1",
            title="Finding the Pet",
            description="The player, An old swordmage, finds a silver egg in an old dungeon.",
            events=[
                ChapterEvent(
                    description="Egg Hatching",
                    trigger_condition=lambda game_state: game_state.pet.age >= 0.5,  # After a few interactions
                    action=lambda game_state: setattr(game_state.pet, 'species', 'drake')
                ),
                ChapterEvent(
                    description="Naming the Drakeling",
                    trigger_condition=lambda game_state: game_state.pet.species == 'drake' and game_state.pet.emotional_state.variables[1].value > 50,  # attachment > 50
                    action=lambda game_state: setattr(game_state.pet, 'name', 'Silverwing')
                )
            ],
            age_increment=1
        ),
        Chapter(
            id="chapter2",
            title="Months of Adventure",
            description="The player, a swordmage, and the drakeling embark on various adventures.",
            events=[
                ChapterEvent(
                    description="First Flight",
                    trigger_condition=lambda game_state: game_state.pet.physical_state.variables[1].value > 70,  # growth > 70
                    action=lambda game_state: print("Silverwing takes its first flight!")
                ),
                ChapterEvent(
                    description="Magical Awakening",
                    trigger_condition=lambda game_state: game_state.pet.physical_state.variables[3].value > 50,  # magical_power > 50
                    action=lambda game_state: print("Silverwing discovers its innate magical abilities!")
                )
            ],
            age_increment=11  # This will bring the drake to 12 months old (1 year)
        ),
        Chapter(
            id="chapter3",
            title="Confronting the Dark Lord's General",
            description="The swordmage and the now young drake face one of the Dark Lord's generals.",
            events=[
                ChapterEvent(
                    description="Epic Battle",
                    trigger_condition=lambda game_state: game_state.pet.age >= 12,  # Drake is now 1 year old
                    action=lambda game_state: print("Silverwing and the swordmage engage in an epic battle against the Dark Lord's general!")
                )
            ],
            age_increment=0
        )
    ]

def main():
    pet = create_initial_pet()
    chapters = create_chapters()
    initial_scenario = generate_dynamic_scenario(pet, None, None, None, chapters[0])
    game = Game(pet, initial_scenario, chapters)

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

        if game.current_chapter_index >= len(game.chapters):
            print("Congratulations! You've completed all chapters.")
            break

if __name__ == "__main__":
    main()