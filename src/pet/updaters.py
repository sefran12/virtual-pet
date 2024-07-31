# src\core\updaters.py
from typing import List, Dict
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

from .memory import Memory
from .states import LatentVariable, EmotionalState, PhysicalState, EmotionalStateDelta, PhysicalStateDelta, PhysicalDescription

load_dotenv(override=True)


    
def apply_emotional_delta(state: EmotionalState, delta: EmotionalStateDelta) -> EmotionalState:
    new_variables = []
    for var in state.variables:
        new_value = var.value + delta.variable_deltas.get(var.name, 0)
        new_variables.append(LatentVariable(var.name, new_value))
    return EmotionalState(new_variables)


def apply_physical_delta(state: PhysicalState, delta: PhysicalStateDelta) -> PhysicalState:
    new_variables = []
    for var in state.variables:
        new_value = var.value + delta.variable_deltas.get(var.name, 0)
        new_variables.append(LatentVariable(var.name, new_value))
    return PhysicalState(variables=new_variables, description=state.description)


def process_interaction_to_emotional_delta(interaction: str) -> EmotionalStateDelta:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_message = """
    You are an AI assistant that interprets interactions with a virtual pet and outputs emotional changes.
    The pet has 5 emotional states: happiness, excitement, calmness, curiosity, and affection.
    Each state can change between -10 and 10 based on the interaction, or remain unchanged (0).
    Output a JSON object with the changes for each emotional state.
    If a state is unaffected by the interaction, set its value to 0.
    Your response should be a valid JSON object.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use the appropriate model
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Interpret this interaction with the virtual pet: {interaction}"}
            ]
        )

        # Check if the response was cut off
        if response.choices[0].finish_reason == "length":
            raise ValueError("Response was cut off. Try a shorter interaction or increase max_tokens.")

        # Parse the JSON response
        delta_dict = json.loads(response.choices[0].message.content)

        # Ensure all expected keys are present
        expected_keys = ["happiness", "excitement", "calmness", "curiosity", "affection"]
        for key in expected_keys:
            if key not in delta_dict:
                delta_dict[key] = 0.0  # Default to no change if missing

        # Create and return the EmotionalStateDelta
        return EmotionalStateDelta(variable_deltas=delta_dict)

    except json.JSONDecodeError:
        print("Error: Invalid JSON response from API")
        return EmotionalStateDelta(variable_deltas={key: 0.0 for key in expected_keys})
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return EmotionalStateDelta(variable_deltas={key: 0.0 for key in expected_keys})


def process_interaction_to_physical_delta(interaction: str) -> PhysicalStateDelta:
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_message = """
    You are an AI assistant that interprets interactions with a virtual pet and outputs physical state changes.
    The pet has 4 physical states: hunger, tiredness, health, and cleanliness.
    Each state can change between -10 and 10 based on the interaction, or remain unchanged (0).
    Output a JSON object with the changes for each physical state.
    If a state is unaffected by the interaction, set its value to 0.
    Your response should be a valid JSON object.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use the appropriate model
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Interpret this interaction with the virtual pet: {interaction}"}
            ]
        )

        if response.choices[0].finish_reason == "length":
            raise ValueError("Response was cut off. Try a shorter interaction or increase max_tokens.")

        delta_dict = json.loads(response.choices[0].message.content)

        expected_keys = ["hunger", "tiredness", "health", "cleanliness"]
        for key in expected_keys:
            if key not in delta_dict:
                delta_dict[key] = 0.0  # Default to no change if missing

        return PhysicalStateDelta(variable_deltas=delta_dict)

    except json.JSONDecodeError:
        print("Error: Invalid JSON response from API")
        return PhysicalStateDelta(variable_deltas={key: 0.0 for key in expected_keys})
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return PhysicalStateDelta(variable_deltas={key: 0.0 for key in expected_keys})

def process_interaction_as_pet_memory(
    interaction: str,
    scenario: str,
    initial_emotional_state: EmotionalState,
    initial_physical_state: PhysicalState,
    emotional_delta: EmotionalStateDelta,
    physical_delta: PhysicalStateDelta
) -> Memory:
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    system_message = """
    Sei un assistente AI che genera ricordi soggettivi per un animale virtuale basati su interazioni e cambiamenti di stato.
    Crea un breve ricordo in prima persona dal punto di vista dell'animale, riflettendo l'interazione e come ha fatto sentire l'animale.
    Il ricordo dovrebbe essere una singola frase, scritta in un linguaggio semplice come se fosse dal punto di vista dell'animale.
    Usa gli stati iniziali e i cambiamenti per informare l'esperienza e la reazione dell'animale.
    La tua risposta dovrebbe essere un oggetto JSON valido con i campi 'memory' e 'importance'.
    Il campo 'memory' dovrebbe contenere il testo del ricordo generato, e il campo 'importance' dovrebbe essere un valore float tra 0 e 1.
    """
    # Prepare the input for the AI
    pet_state_info = f"""
    Stato emotivo iniziale: {initial_emotional_state}
    Stato fisico iniziale: {initial_physical_state}
    Cambiamenti emotivi: {emotional_delta.variable_deltas}
    Cambiamenti fisici: {physical_delta.variable_deltas}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Usa il modello appropriato
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Scenario: {scenario}\nInterazione: {interaction}\n{pet_state_info}"}
            ]
        )
        if response.choices[0].finish_reason == "length":
            raise ValueError("La risposta è stata troncata. Prova una interazione più breve o aumenta max_tokens.")
        memory_data = json.loads(response.choices[0].message.content)
       
        # Assuming the AI returns a JSON object with 'memory' and 'importance' fields
        memory_content = memory_data.get('memory', "Ricordo qualcosa che è successo, ma è sfocato.")
        memory_importance = float(memory_data.get('importance', 0.5))  # Default to 0.5 if not provided
        return Memory(content=memory_content, importance=memory_importance)
    except json.JSONDecodeError:
        print("Errore: Risposta JSON non valida dall'API")
        return Memory(content="Non sono sicuro di cosa sia successo.", importance=0.1)
    except Exception as e:
        print(f"Si è verificato un errore: {str(e)}")
        return Memory(content="È successo qualcosa, ma non riesco a ricordare bene.", importance=0.1)


def process_interaction_for_pet_response(
    interaction: str,
    initial_emotional_state: EmotionalState,
    initial_physical_state: PhysicalState,
    emotional_delta: EmotionalStateDelta,
    physical_delta: PhysicalStateDelta,
    last_memory: Memory,
    physical_description: PhysicalDescription
) -> str:
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_message = """
    You are an AI assistant that generates responses for a virtual pet based on interactions, state changes, and context.
    The pet cannot talk, so the response should be a description of the pet's actions, behaviors, and apparent emotions.
    Use the initial states, changes, last memory, and physical description to create a single sentence that encondes a vivid and engaging response, written with a succint, clear prose without complicated words.
    Your response should be a valid JSON object with a single 'response' field containing the pet's reaction as a string.
    """

    pet_context = f"""
    Physical Description: {physical_description}
    Initial Emotional State: {initial_emotional_state}
    Initial Physical State: {initial_physical_state}
    Emotional Changes: {emotional_delta.variable_deltas}
    Physical Changes: {physical_delta.variable_deltas}
    Last Memory: {last_memory.content if last_memory else 'No recent memory'}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use the appropriate model
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Interaction: {interaction}\n{pet_context}"}
            ]
        )

        if response.choices[0].finish_reason == "length":
            raise ValueError("Response was cut off. Try a shorter interaction or increase max_tokens.")

        response_data = json.loads(response.choices[0].message.content)
        return response_data.get('response', "The pet reacts, but it's unclear how.")

    except json.JSONDecodeError:
        print("Error: Invalid JSON response from API")
        return "The pet seems confused by what just happened."
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return "The pet's reaction is hard to interpret."
    
def update_pet_physical_description(pet: 'Pet', chapter_narrative: List[Dict[str, str]]) -> PhysicalDescription:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_message = f"""
    You are an AI assistant that updates the physical description of a virtual pet based on its experiences throughout a chapter.
    Consider the pet's current state, age, and the events it has gone through to create a new, evolved description.

    Current pet state:
    {pet.summarize_state()}

    Chapter narrative summary:
    {json.dumps(chapter_narrative, indent=2)}

    Generate a new physical description for the pet, including possible changes to its species, color, size, and distinctive features.
    Your response should be a valid JSON object with 'species', 'color', 'size', and 'distinctive_features' fields.
    The 'distinctive_features' field should be a list of strings.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": "Generate an updated physical description for the pet based on its experiences in this chapter."}
            ]
        )

        new_description_data = json.loads(response.choices[0].message.content)
        
        return PhysicalDescription(
            species=new_description_data['species'],
            color=new_description_data['color'],
            size=new_description_data['size'],
            distinctive_features=new_description_data['distinctive_features']
        )

    except Exception as e:
        print(f"An error occurred while updating the pet's physical description: {str(e)}")
        return pet.physical_state.description  # Return the current description if there's an error
