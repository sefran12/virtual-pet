# src\narration\scenario.py
from dataclasses import dataclass, field
from typing import List, Optional
from ..game.choices import ScenarioChoice
import random
import json
from openai import OpenAI
import os
from dotenv import load_dotenv
from src.utils.config import AIConfig

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
    current_chapter: 'Chapter',
    ai_config: AIConfig
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

    client = ai_config.get_client()

    system_message = f"""
    Sei un assistente AI che genera scenari dinamici per un gioco di animali virtuali.
    Usa il modello fornito, lo stato attuale dell'animale, lo scenario precedente, l'ultima interazione, la risposta dell'animale e le informazioni sul capitolo attuale per creare uno scenario unico e coinvolgente.
    Assicurati che la narrazione fluisca continuamente dallo scenario e dall'interazione precedenti, senza iniziare arbitrariamente un nuovo giorno a meno che non sia narrativamente appropriato.
    Stato attuale dell'animale:
    {pet.summarize_state()}
    Scenario precedente:
    {previous_scenario.description if previous_scenario else "Nessuno scenario precedente"}
    Ultima interazione:
    {last_interaction if last_interaction else "Nessuna interazione precedente"}
    Ultima risposta dell'animale:
    {last_pet_response if last_pet_response else "Nessuna risposta precedente dell'animale"}
    Capitolo attuale:
    Titolo: {current_chapter.title}
    Descrizione: {current_chapter.description}
    Eventi completati: {', '.join(current_chapter.completed_events)}
    Evento casuale (se presente):
    {random_event.description if random_event else "Nessun evento casuale"}
    Modello di scenario:
    {template.description_template}
    Genera una descrizione e delle scelte basate su queste informazioni.
    La tua risposta dovrebbe essere un oggetto JSON valido con campi 'description' e 'choices'.
    Il campo 'choices' dovrebbe essere una lista di oggetti, ciascuno con campi 'text' e 'action'.
    Incorpora l'evento casuale nello scenario se presente.
    Assicurati che lo scenario sia allineato con la narrazione del capitolo attuale e lo sviluppo dell'animale.
    Mantieni la continuità narrativa dallo scenario e dall'interazione precedenti.
    """

    try:
        response = client.chat.completions.create(
            model=ai_config.get_model(),
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": "Genera uno scenario basato sulle informazioni fornite."}
            ]
        )

        scenario_data = json.loads(response.choices[0].message.content)
        
        choices = [
            ScenarioChoice(text=choice['text'], action=lambda game, msg, scenario, c=choice['action']: game.update_pet(c, scenario))
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
