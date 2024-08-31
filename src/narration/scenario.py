from dataclasses import dataclass, field
from typing import List, Optional
from ..game.choices import ScenarioChoice
import random
import json
from openai import OpenAI
import os
from dotenv import load_dotenv
from src.utils.resource_manager import ResourceManager

load_dotenv()
resource_manager = ResourceManager()

@dataclass
class Scenario:
    id: str
    description: str
    choices: List[ScenarioChoice]

@dataclass
class ScenarioTemplate:
    id: str
    description_template: str
    choice_templates: List[dict]

@dataclass
class RandomEvent:
    description: str
    probability: float

def load_scenario_templates(file_path: str) -> List[ScenarioTemplate]:
    with open(file_path, 'r') as f:
        templates_data = json.load(f)
    return [ScenarioTemplate(**template) for template in templates_data]

def load_random_events(file_path: str) -> List[RandomEvent]:
    with open(file_path, 'r') as f:
        events_data = json.load(f)
    return [RandomEvent(**event) for event in events_data]

def generate_dynamic_scenario(
    pet: 'Pet',
    previous_scenario: Optional[Scenario],
    last_interaction: Optional[str],
    last_pet_response: Optional[str],
    current_chapter: 'Chapter',
    language: str = 'english'
) -> Scenario:
    templates = load_scenario_templates('data/scenario_templates.json')
    random_events = load_random_events('data/random_events.json')
    template = random.choice(templates)

    # Check for a random event
    random_event = None
    for event in random_events:
        if random.random() < event.probability:
            random_event = event
            break

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_message = resource_manager.get_prompt('scenario', 'generate_dynamic_scenario', language).format(
        pet_state=pet.summarize_state(),
        previous_scenario=previous_scenario.description if previous_scenario else "No previous scenario",
        last_interaction=last_interaction if last_interaction else "No previous interaction",
        last_pet_response=last_pet_response if last_pet_response else "No previous pet response",
        chapter_title=current_chapter.title,
        chapter_description=current_chapter.description,
        completed_events=', '.join(current_chapter.completed_events),
        random_event=random_event.description if random_event else "No random event",
        scenario_template=template.description_template
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": "Generate a scenario based on the provided information."}
            ]
        )

        scenario_data = json.loads(response.choices[0].message.content)
        
        choices = [
            ScenarioChoice(text=choice['text'], action=lambda game, msg, c=choice['action']: game.update_pet(c))
            for choice in scenario_data['choices']
        ]

        return Scenario(
            id=template.id,
            description=scenario_data['description'],
            choices=choices
        )

    except Exception as e:
        print(f"An error occurred while generating the scenario: {str(e)}")
        return Scenario(
            id="error",
            description="An error occurred while generating the scenario.",
            choices=[ScenarioChoice(text="Continue", action=lambda game, msg: None)]
        )