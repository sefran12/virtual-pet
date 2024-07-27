
# src/game/scenario.py
from dataclasses import dataclass, field
from typing import List, Optional
from .choices import ScenarioChoice
import random
import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

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

from dataclasses import dataclass, field
from typing import List, Optional
from .choices import ScenarioChoice
import random
import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

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
    current_chapter: 'Chapter'
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

    system_message = f"""
    You are an AI assistant that generates dynamic scenarios for a virtual pet game.
    Use the given template, the pet's current state, previous scenario, last interaction, pet response, and current chapter information to create a unique and engaging scenario.
    Ensure the narrative flows continuously from the previous scenario and interaction, without arbitrarily starting a new day unless it's narratively appropriate.

    Pet's current state:
    {pet.summarize_state()}

    Previous scenario:
    {previous_scenario.description if previous_scenario else "No previous scenario"}

    Last interaction:
    {last_interaction if last_interaction else "No previous interaction"}

    Last pet response:
    {last_pet_response if last_pet_response else "No previous pet response"}

    Current Chapter:
    Title: {current_chapter.title}
    Description: {current_chapter.description}
    Completed Events: {', '.join(current_chapter.completed_events)}

    Random event (if any):
    {random_event.description if random_event else "No random event"}

    Scenario Template:
    {template.description_template}

    Generate a description and choices based on this information.
    Your response should be a valid JSON object with 'description' and 'choices' fields.
    The 'choices' field should be a list of objects, each with 'text' and 'action' fields.
    Incorporate the random event into the scenario if one is present.
    Ensure the scenario aligns with the current chapter's narrative and the pet's development.
    Maintain narrative continuity from the previous scenario and interaction.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": "Generate a scenario based on the given information."}
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