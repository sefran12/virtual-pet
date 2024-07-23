# src/utils/formatters.py
def format_pet_state(pet):
    formatted_state = f"""
{pet.name}'s Current State:
-----------------------------
Emotional State:
{', '.join([f'{v.name}: {v.value}' for v in pet.emotional_state.variables])}

Physical State:
{', '.join([f'{v.name}: {v.value}' for v in pet.physical_state.variables])}

Description: {pet.physical_state.description.species.capitalize()} - {pet.physical_state.description.color}, {pet.physical_state.description.size} - Age {pet.age} years
Distinctive features: {', '.join(pet.physical_state.description.distinctive_features)}
    """
    return formatted_state.strip()


def format_pet_memories(pet):
    short_term = "\n".join(
        [f"- {memory.content}" for memory in pet.short_term_memory.events[-5:]]
    )
    long_term_people = "\n".join(
        [
            f"- {key}: {memory.content}"
            for key, memory in pet.long_term_memory.people.items()
        ]
    )
    long_term_events = "\n".join(
        [
            f"- {key}: {memory.content}"
            for key, memory in pet.long_term_memory.events.items()
        ]
    )
    long_term_places = "\n".join(
        [
            f"- {key}: {memory.content}"
            for key, memory in pet.long_term_memory.places.items()
        ]
    )

    formatted_memories = f"""
{pet.name}'s Memories:
-----------------------------
Recent Memories (last 5):
{short_term}

Long-term Memories:
People:
{long_term_people}

Events:
{long_term_events}

Places:
{long_term_places}
    """
    return formatted_memories.strip()
