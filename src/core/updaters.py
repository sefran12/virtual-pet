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
    initial_emotional_state: EmotionalState,
    initial_physical_state: PhysicalState,
    emotional_delta: EmotionalStateDelta,
    physical_delta: PhysicalStateDelta
) -> Memory:
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_message = """
    You are an AI assistant that generates subjective memories for a virtual pet based on interactions and state changes.
    Create a short, first-person memory from the pet's perspective, reflecting the interaction and how it made the pet feel.
    The memory should be a single sentence, written in simple language as if from the pet's point of view.
    Use the initial states and the changes to inform the pet's experience and reaction.
    Your response should be a valid JSON object with 'memory' and 'importance' fields.
    The 'memory' field should contain the generated memory text, and the 'importance' field should be a float between 0 and 1.
    """


    # Prepare the input for the AI
    pet_state_info = f"""
    Initial Emotional State: {initial_emotional_state}
    Initial Physical State: {initial_physical_state}
    Emotional Changes: {emotional_delta.variable_deltas}
    Physical Changes: {physical_delta.variable_deltas}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use the appropriate model
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Interaction: {interaction}\n{pet_state_info}"}
            ]
        )

        if response.choices[0].finish_reason == "length":
            raise ValueError("Response was cut off. Try a shorter interaction or increase max_tokens.")

        memory_data = json.loads(response.choices[0].message.content)
        
        # Assuming the AI returns a JSON object with 'memory' and 'importance' fields
        memory_content = memory_data.get('memory', "I remember something happening, but it's fuzzy.")
        memory_importance = float(memory_data.get('importance', 0.5))  # Default to 0.5 if not provided

        return Memory(content=memory_content, importance=memory_importance)

    except json.JSONDecodeError:
        print("Error: Invalid JSON response from API")
        return Memory(content="I'm not sure what happened.", importance=0.1)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return Memory(content="Something happened, but I can't quite remember.", importance=0.1)
    
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