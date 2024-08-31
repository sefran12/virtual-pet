import textwrap
import shutil
from colorama import Fore, Back, Style, init

from src.pet.pet import Pet
from src.pet.states import EmotionalState, PhysicalState, PhysicalDescription, LatentVariable
from src.pet.memory import LongTermMemory, ShortTermMemory
from src.game.game import Game
from src.narration.scenario import generate_dynamic_scenario
from src.narration.chapter import Chapter, ChapterEvent
from src.game.game_state import GameState
from src.utils.resource_manager import ResourceManager

resource_manager = ResourceManager()
language = 'english'  # Default language, can be changed to 'spanish' or 'italian'

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
            title=resource_manager.get_prompt('main', 'chapter_titles.chapter1', language),
            description=resource_manager.get_prompt('main', 'chapter_descriptions.chapter1', language),
            events=[
                ChapterEvent(
                    description="Schiusura dell'uovo",
                    trigger_condition=lambda game_state: game_state.pet.age >= 0.5,
                    action=lambda game_state: setattr(game_state.pet, 'species', 'drago')
                ),
                ChapterEvent(
                    description="Dare un nome al piccolo drago",
                    trigger_condition=lambda game_state: game_state.pet.species == 'drago' and game_state.pet.emotional_state.variables[1].value > 50,
                    action=lambda game_state: setattr(game_state.pet, 'name', resource_manager.get_prompt('main', 'dragon_name', language))
                )
            ],
            age_increment=1
        ),
        Chapter(
            id="chapter2",
            title=resource_manager.get_prompt('main', 'chapter_titles.chapter2', language),
            description=resource_manager.get_prompt('main', 'chapter_descriptions.chapter2', language),
            events=[
                ChapterEvent(
                    description="Primo volo",
                    trigger_condition=lambda game_state: game_state.pet.physical_state.variables[1].value > 70,
                    action=lambda game_state: print(resource_manager.get_prompt('main', 'first_flight', language))
                ),
                ChapterEvent(
                    description="Risveglio magico",
                    trigger_condition=lambda game_state: game_state.pet.physical_state.variables[3].value > 50,
                    action=lambda game_state: print(resource_manager.get_prompt('main', 'magical_awakening', language))
                )
            ],
            age_increment=11
        ),
        Chapter(
            id="chapter3",
            title=resource_manager.get_prompt('main', 'chapter_titles.chapter3', language),
            description=resource_manager.get_prompt('main', 'chapter_descriptions.chapter3', language),
            events=[
                ChapterEvent(
                    description="Battaglia epica",
                    trigger_condition=lambda game_state: game_state.pet.age >= 12,
                    action=lambda game_state: print(resource_manager.get_prompt('main', 'epic_battle', language))
                )
            ],
            age_increment=0
        )
    ]

def get_console_width():
    return shutil.get_terminal_size().columns

def print_wrapped(text, color=Fore.WHITE, width=None):
    if width is None:
        width = int(get_console_width() * 0.8)
    
    for line in textwrap.wrap(text, width=width):
        justified_line = line.ljust(width)
        print(f"{color}{justified_line}{Style.RESET_ALL}")

def print_scenario(scenario):
    width = int(get_console_width() * 0.8)
    print(f"\n{Fore.BLUE}{Style.BRIGHT}{'=' * width}{Style.RESET_ALL}")
    print_wrapped(scenario.description, Fore.CYAN)
    print(f"{Fore.BLUE}{Style.BRIGHT}{'=' * width}{Style.RESET_ALL}\n")

def print_choices(choices):
    print(f"{Fore.MAGENTA}{resource_manager.get_prompt('main', 'available_choices', language)}{Style.RESET_ALL}")
    for i, choice in enumerate(choices, 1):
        print_wrapped(f"{i}. {choice.text}", Fore.YELLOW)
    print_wrapped(f"{len(choices) + 1}. {resource_manager.get_prompt('main', 'free_action', language)}", Fore.YELLOW)

def print_additional_options():
    print(f"\n{Fore.MAGENTA}{resource_manager.get_prompt('main', 'additional_options', language)}{Style.RESET_ALL}")
    state_command = resource_manager.get_prompt('main', 'state_command', language)
    memories_command = resource_manager.get_prompt('main', 'memories_command', language)
    quit_command = resource_manager.get_prompt('main', 'quit_command', language)
    
    print_wrapped(resource_manager.get_prompt('main', 'state_description', language).format(command=Fore.YELLOW + state_command + Style.RESET_ALL))
    print_wrapped(resource_manager.get_prompt('main', 'memories_description', language).format(command=Fore.YELLOW + memories_command + Style.RESET_ALL))
    print_wrapped(resource_manager.get_prompt('main', 'quit_description', language).format(command=Fore.YELLOW + quit_command + Style.RESET_ALL))

def print_pet_response(response):
    print(f"\n{Fore.GREEN}{resource_manager.get_prompt('main', 'pet_response', language)}{Style.RESET_ALL}")
    print_wrapped(response, Fore.WHITE)

def print_pet_state(state):
    print(f"\n{Fore.MAGENTA}{resource_manager.get_prompt('main', 'pet_state', language)}{Style.RESET_ALL}")
    print_wrapped(state, Fore.WHITE)

def main():
    init(autoreset=True)  # Initialize colorama
    pet = create_initial_pet()
    chapters = create_chapters()
    initial_scenario = generate_dynamic_scenario(pet, None, None, None, chapters[0], language)
    game = Game(pet, initial_scenario, chapters)
    
    while True:
        print_scenario(game.current_scenario)
        print_choices(game.current_scenario.choices)
        print_additional_options()
        
        user_input = input(f"{Fore.YELLOW}{resource_manager.get_prompt('main', 'user_input_prompt', language)}{Style.RESET_ALL}")
        if user_input.lower() == resource_manager.get_prompt('main', 'quit_command', language):
            break
        
        result = game.process_message(user_input)
        
        if 'special_action' in result:
            print_wrapped(result['content'], Fore.CYAN)
        else:
            print_pet_response(result['pet_response'])
            print_pet_state(result['pet_state'])
        
        if game.current_chapter_index >= len(game.chapters):
            print_wrapped(f"\n{Fore.GREEN}{Style.BRIGHT}{resource_manager.get_prompt('main', 'game_complete', language)}{Style.RESET_ALL}")
            break

if __name__ == "__main__":
    main()