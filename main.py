# main.py

import textwrap
from colorama import Fore, Back, Style, init

from src.pet.pet import Pet
from src.pet.states import EmotionalState, PhysicalState, PhysicalDescription, LatentVariable
from src.pet.memory import LongTermMemory, ShortTermMemory
from src.game.game import Game
from src.narration.scenario import generate_dynamic_scenario
from src.narration.chapter import Chapter, ChapterEvent
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
            title="Alla ricerca dell'animale",
            description="Il giocatore, un vecchio magospada, trova un uovo d'argento in un vecchio dungeon.",
            events=[
                ChapterEvent(
                    description="Schiusura dell'uovo",
                    trigger_condition=lambda game_state: game_state.pet.age >= 0.5,  # Dopo alcune interazioni
                    action=lambda game_state: setattr(game_state.pet, 'species', 'drago')
                ),
                ChapterEvent(
                    description="Dare un nome al piccolo drago",
                    trigger_condition=lambda game_state: game_state.pet.species == 'drago' and game_state.pet.emotional_state.variables[1].value > 50,  # attaccamento > 50
                    action=lambda game_state: setattr(game_state.pet, 'name', "Ala d'Argento")
                )
            ],
            age_increment=1
        ),
        Chapter(
            id="chapter2",
            title="Mesi di avventura",
            description="Il giocatore, un magospada, e il piccolo drago intraprendono varie avventure.",
            events=[
                ChapterEvent(
                    description="Primo volo",
                    trigger_condition=lambda game_state: game_state.pet.physical_state.variables[1].value > 70,  # crescita > 70
                    action=lambda game_state: print("Ala d'Argento fa il suo primo volo!")
                ),
                ChapterEvent(
                    description="Risveglio magico",
                    trigger_condition=lambda game_state: game_state.pet.physical_state.variables[3].value > 50,  # potere magico > 50
                    action=lambda game_state: print("Ala d'Argento scopre le sue abilità magiche innate!")
                )
            ],
            age_increment=11  # Questo porterà il drago a 12 mesi di età (1 anno)
        ),
        Chapter(
            id="chapter3",
            title="Affrontare il generale del Signore Oscuro",
            description="Il magospada e il giovane drago affrontano uno dei generali del Signore Oscuro.",
            events=[
                ChapterEvent(
                    description="Battaglia epica",
                    trigger_condition=lambda game_state: game_state.pet.age >= 12,  # Il drago ha ora 1 anno
                    action=lambda game_state: print("Ala d'Argento e il magospada si impegnano in una battaglia epica contro il generale del Signore Oscuro!")
                )
            ],
            age_increment=0
        )
    ]


def main():
    init(autoreset=True)  # Initialize colorama
    pet = create_initial_pet()
    chapters = create_chapters()
    initial_scenario = generate_dynamic_scenario(pet, None, None, None, chapters[0])
    game = Game(pet, initial_scenario, chapters)
    
    while True:
        print_scenario(game.current_scenario)
        print_choices(game.current_scenario.choices)
        print_additional_options()
        
        user_input = input(f"{Fore.YELLOW}Inserisci la tua scelta: {Style.RESET_ALL}")
        if user_input.lower() == 'quit':
            break
        
        result = game.process_message(user_input)
        
        if 'special_action' in result:
            print_wrapped(result['content'], Fore.CYAN)
        else:
            print_pet_response(result['pet_response'])
            print_pet_state(result['pet_state'])
        
        if game.current_chapter_index >= len(game.chapters):
            print(f"\n{Fore.GREEN}{Style.BRIGHT}Congratulazioni! Hai completato tutti i capitoli.{Style.RESET_ALL}")
            break

def print_scenario(scenario):
    print(f"\n{Fore.BLUE}{Style.BRIGHT}{'=' * 50}{Style.RESET_ALL}")
    print_wrapped(scenario.description, Fore.CYAN)
    print(f"{Fore.BLUE}{Style.BRIGHT}{'=' * 50}{Style.RESET_ALL}\n")

def print_choices(choices):
    print(f"{Fore.MAGENTA}Scelte disponibili:{Style.RESET_ALL}")
    for i, choice in enumerate(choices, 1):
        print(f"{Fore.YELLOW}{i}. {Style.RESET_ALL}{choice.text}")
    print(f"{Fore.YELLOW}{len(choices) + 1}. {Style.RESET_ALL}[Azione Libera]")

def print_additional_options():
    print(f"\n{Fore.MAGENTA}Opzioni aggiuntive:{Style.RESET_ALL}")
    print(f"- Digita '{Fore.YELLOW}state{Style.RESET_ALL}' per vedere lo stato dettagliato dell'animale")
    print(f"- Digita '{Fore.YELLOW}memories{Style.RESET_ALL}' per vedere i ricordi dell'animale")
    print(f"- Digita '{Fore.YELLOW}quit{Style.RESET_ALL}' per uscire dal gioco")

def print_pet_response(response):
    print(f"\n{Fore.GREEN}Risposta dell'animale:{Style.RESET_ALL}")
    print_wrapped(response, Fore.WHITE)

def print_pet_state(state):
    print(f"\n{Fore.MAGENTA}Stato dell'animale:{Style.RESET_ALL}")
    print_wrapped(state, Fore.WHITE)

def print_wrapped(text, color=Fore.WHITE, width=70):
    for line in textwrap.wrap(text, width=width):
        print(f"{color}{line}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
