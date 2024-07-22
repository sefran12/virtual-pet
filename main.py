from src.core.pet import Pet
from src.core.states import EmotionalState, PhysicalState, PhysicalDescription, LatentVariable
from src.core.memory import LongTermMemory, ShortTermMemory
from src.game.game import Game
from src.game.scenario import Scenario
from src.game.choices import ScenarioChoice

def create_sample_pet():
    return Pet(
        name="Whiskers",
        age=3,
        emotional_state=EmotionalState([
            LatentVariable("happiness", 0),
            LatentVariable("excitement", 0),
            LatentVariable("calmness", 0),
            LatentVariable("curiosity", 0),
            LatentVariable("affection", 0)
        ]),
        physical_state=PhysicalState(
            variables=[
                LatentVariable("hunger", 0),
                LatentVariable("tiredness", 0),
                LatentVariable("health", 100),
                LatentVariable("cleanliness", 100)
            ],
            description=PhysicalDescription(
                species="cat",
                color="orange tabby",
                size="medium",
                distinctive_features=["bright green eyes", "fluffy tail"]
            )
        ),
        long_term_memory=LongTermMemory(),
        short_term_memory=ShortTermMemory()
    )

def main():
    pet = create_sample_pet()

    # Define choice actions
    def feed_pet(game):
        game.update_pet("Feed the pet a healthy meal")
        game.change_scenario("play_time")

    def play_with_pet(game):
        game.update_pet("Play with the pet using a toy")
        game.change_scenario("nap_time")

    def let_pet_nap(game):
        game.update_pet("Let the pet take a nap")
        game.change_scenario("grooming_time")

    def groom_pet(game):
        game.update_pet("Groom the pet gently")
        game.change_scenario("feeding_time")

    def ignore_pet(game):
        game.update_pet("Ignore the pet")
        game.change_scenario("feeding_time")

    def auto_update_hunger(game):
        hunger = next(var for var in game.pet.physical_state.variables if var.name == "hunger")
        hunger.value += 10
        print("Your pet is getting hungrier...")

    choice_actions = {
        "feed_pet": feed_pet,
        "play_with_pet": play_with_pet,
        "let_pet_nap": let_pet_nap,
        "groom_pet": groom_pet,
        "ignore_pet": ignore_pet,
        "auto_update_hunger": auto_update_hunger
    }

    # Load scenarios from JSON
    game = Game.from_json(pet, "data/scenarios.json", choice_actions)

    game.start()

if __name__ == "__main__":
    main()