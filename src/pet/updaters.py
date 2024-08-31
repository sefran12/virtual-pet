from typing import List, Dict
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

from .memory import Memory
from .states import LatentVariable, EmotionalState, PhysicalState, EmotionalStateDelta, PhysicalStateDelta, PhysicalDescription
from src.utils.resource_manager import ResourceManager

load_dotenv(override=True)
resource_manager = ResourceManager()

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

def process_interaction_to_emotional_delta(interaction: str, language: str = 'english') -> EmotionalStateDelta:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_message = resource_manager.get_prompt('updaters', 'process_interaction_to_emotional_delta', language)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Interpret this interaction with the virtual pet: {interaction}"}
            ]
        )

        if response.choices[0].finish_reason == "length":
            raise ValueError("Response was cut off. Try a shorter interaction or increase max_tokens.")

        delta_dict = json.loads(response.choices[0].message.content)

        expected_keys = ["happiness", "excitement", "calmness", "curiosity", "affection"]
        for key in expected_keys:
            if key not in delta_dict:
                delta_dict[key] = 0.0

        return EmotionalStateDelta(variable_deltas=delta_dict)

    except json.JSONDecodeError:
        print("Error: Invalid JSON response from API")
        return EmotionalStateDelta(variable_deltas={key: 0.0 for key in expected_keys})
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return EmotionalStateDelta(variable_deltas={key: 0.0 for key in expected_keys})

def process_interaction_to_physical_delta(interaction: str, language: str = 'english') -> PhysicalStateDelta:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_message = resource_manager.get_prompt('updaters', 'process_interaction_to_physical_delta', language)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
                delta_dict[key] = 0.0

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
    physical_delta: PhysicalStateDelta,
    language: str = 'english'
) -> Memory:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    system_message = resource_manager.get_prompt('updaters', 'process_interaction_as_pet_memory', language)

    pet_state_info = f"""
    Initial Emotional State: {initial_emotional_state}
    Initial Physical State: {initial_physical_state}
    Emotional Changes: {emotional_delta.variable_deltas}
    Physical Changes: {physical_delta.variable_deltas}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Scenario: {scenario}\nInteraction: {interaction}\n{pet_state_info}"}
            ]
        )
        if response.choices[0].finish_reason == "length":
            raise ValueError("Response was cut off. Try a shorter interaction or increase max_tokens.")
        memory_data = json.loads(response.choices[0].message.content)
       
        memory_content = memory_data.get('memory', "I remember something happened, but it's fuzzy.")
        memory_importance = float(memory_data.get('importance', 0.5))
        return Memory(content=memory_content, importance=memory_importance)
    except json.JSONDecodeError:
        print("Error: Invalid JSON response from API")
        return Memory(content="I'm not sure what happened.", importance=0.1)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return Memory(content="Something happened, but I can't remember clearly.", importance=0.1)

def process_interaction_for_pet_response(
    response_prompt: str,
    interaction: str,
    initial_emotional_state: EmotionalState,
    initial_physical_state: PhysicalState,
    emotional_delta: EmotionalStateDelta,
    physical_delta: PhysicalStateDelta,
    last_memory: Memory,
    physical_description: PhysicalDescription
) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": response_prompt},
                {"role": "user", "content": f"Interaction: {interaction}\n{pet_context}"}
            ]
        )

        if response.choices[0].finish_response_prompt == "length":
            raise ValueError("Response was cut off. Try a shorter interaction or increase max_tokens.")

        response_data = json.loads(response.choices[0].message.content)
        return response_data.get('response', "The pet reacts, but it's unclear how.")

    except json.JSONDecodeError:
        print("Error: Invalid JSON response from API")
        return "The pet seems confused by what just happened."
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return "The pet's reaction is hard to interpret."
    
def update_pet_physical_description(pet: 'Pet', chapter_narrative: List[Dict[str, str]], language: str = 'english') -> PhysicalDescription:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_message = resource_manager.get_prompt('updaters', 'update_pet_physical_description', language)

    context = f"""
    Current pet state:
    {pet.summarize_state()}

    Chapter narrative summary:
    {json.dumps(chapter_narrative, indent=2)}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"{context}\nGenerate an updated physical description for the pet based on its experiences in this chapter."}
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
