import random
from dataclasses import dataclass, field
from typing import List, Dict, Callable, Optional, Any
import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Pet Module
@dataclass
class LatentVariable:
    name: str
    value: float

    def __post_init__(self):
        self.value = max(-100, min(100, self.value))

@dataclass
class EmotionalState:
    variables: List[LatentVariable]

@dataclass
class PhysicalDescription:
    species: str
    color: str
    size: str
    distinctive_features: List[str]

@dataclass
class PhysicalState:
    variables: List[LatentVariable]
    description: PhysicalDescription

@dataclass
class Memory:
    content: str
    importance: float

@dataclass
class Pet:
    name: str
    age: int
    species: str
    emotional_state: EmotionalState
    physical_state: PhysicalState
    memories: List[Memory] = field(default_factory=list)

    def process_interaction(self, interaction: str, story_state: 'StoryState') -> str:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        system_message = f"""
        You are an AI that processes pet interactions in a story.
        Current pet state: {self.summarize_state()}
        Story context: {json.dumps(story_state.to_dict())}
        
        Based on the interaction, update the pet's emotional and physical state, create a new memory,
        and generate the pet's response. Return a JSON object with 'emotional_delta', 'physical_delta',
        'new_memory', and 'pet_response' fields.
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"Process this interaction: {interaction}"}
                ]
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Update states
            for var in self.emotional_state.variables:
                var.value += result['emotional_delta'].get(var.name, 0)
            for var in self.physical_state.variables:
                var.value += result['physical_delta'].get(var.name, 0)
            
            # Add new memory
            self.memories.append(Memory(**result['new_memory']))
            
            return result['pet_response']
        
        except Exception as e:
            print(f"An error occurred while processing pet interaction: {str(e)}")
            return "The pet reacts, but it's unclear how."

    def summarize_state(self) -> str:
        return f"""
        Name: {self.name}
        Age: {self.age}
        Species: {self.species}
        Emotional State: {', '.join([f'{v.name}: {v.value}' for v in self.emotional_state.variables])}
        Physical State: {', '.join([f'{v.name}: {v.value}' for v in self.physical_state.variables])}
        Description: {self.physical_state.description.species.capitalize()} - {self.physical_state.description.color}, {self.physical_state.description.size}
        Distinctive features: {', '.join(self.physical_state.description.distinctive_features)}
        Recent memory: {self.memories[-1].content if self.memories else 'No recent memories'}
        """

# Existing Chapter Generation System (with modifications)

@dataclass
class Event:
    description: str
    trigger_condition: Callable[['StoryState'], bool]
    action: Callable[['StoryState'], None]

@dataclass
class Chapter:
    id: str
    title: str
    description: str
    events: List[Event]
    completed_events: List[str] = field(default_factory=list)
    narrative_summary: List[Dict[str, str]] = field(default_factory=list)

    def add_to_narrative(self, scene: str, player_action: str, outcome: str, pet_reaction: str):
        self.narrative_summary.append({
            "scene": scene,
            "player_action": player_action,
            "outcome": outcome,
            "pet_reaction": pet_reaction
        })

    def update(self, story_state: 'StoryState') -> List[Event]:
        triggered_events = []
        for event in self.events:
            if event.description not in self.completed_events and event.trigger_condition(story_state):
                event.action(story_state)
                self.completed_events.append(event.description)
                triggered_events.append(event)
        return triggered_events

    def is_completed(self) -> bool:
        return len(self.completed_events) == len(self.events)

@dataclass
class StoryState:
    current_chapter: Chapter
    player_attributes: Dict[str, int]
    world_state: Dict[str, Any]
    inventory: List[str]
    pet: Pet

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_chapter": self.current_chapter.title,
            "player_attributes": self.player_attributes,
            "world_state": self.world_state,
            "inventory": self.inventory,
            "pet_summary": self.pet.summarize_state()
        }

@dataclass
class Scene:
    id: str
    description: str
    choices: List[Dict[str, str]]

def generate_dynamic_scene(story_state: StoryState) -> Scene:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_message = f"""
    You are an AI storyteller generating dynamic scenes for an interactive story with a pet companion.
    Use the current chapter information, player attributes, world state, inventory, and pet state to create a unique and engaging scene.
    
    Current Chapter: {story_state.current_chapter.title}
    Chapter Description: {story_state.current_chapter.description}
    Player Attributes: {json.dumps(story_state.player_attributes)}
    World State: {json.dumps(story_state.world_state)}
    Inventory: {', '.join(story_state.inventory)}
    Pet State: {story_state.pet.summarize_state()}
    
    Generate a scene description and 3 choices for the player. Include the pet in the scene description or choices where appropriate.
    Your response should be a valid JSON object with 'description' and 'choices' fields.
    The 'choices' field should be a list of objects, each with 'text' and 'action' fields.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": "Generate a dynamic scene for the current story state."}
            ]
        )

        scene_data = json.loads(response.choices[0].message.content)
        
        return Scene(
            id=f"scene_{len(story_state.current_chapter.narrative_summary) + 1}",
            description=scene_data['description'],
            choices=scene_data['choices']
        )

    except Exception as e:
        print(f"An error occurred while generating the scene: {str(e)}")
        return Scene(
            id="error_scene",
            description="An error occurred while generating the scene.",
            choices=[{"text": "Continue", "action": "The story continues despite the setback."}]
        )

class ChapterGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_chapter(self, story_context: Dict[str, Any]) -> Chapter:
        system_message = f"""
        You are an AI storyteller generating a new chapter for an interactive story with a pet companion.
        Use the provided story context to create a compelling chapter with events and challenges that involve both the player and their pet.
        
        Story Context: {json.dumps(story_context)}
        
        Generate a chapter with a title, description, and 3-5 key events.
        Your response should be a valid JSON object with 'title', 'description', and 'events' fields.
        The 'events' field should be a list of objects, each with 'description' and 'trigger_condition' fields.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": "Generate a new chapter for the story."}
                ]
            )

            chapter_data = json.loads(response.choices[0].message.content)
            
            events = [
                Event(
                    description=event['description'],
                    trigger_condition=lambda state, desc=event['description']: desc in state.current_chapter.description,
                    action=lambda state: print(f"Event triggered: {event['description']}")
                )
                for event in chapter_data['events']
            ]

            return Chapter(
                id=f"chapter_{len(story_context.get('completed_chapters', [])) + 1}",
                title=chapter_data['title'],
                description=chapter_data['description'],
                events=events
            )

        except Exception as e:
            print(f"An error occurred while generating the chapter: {str(e)}")
            return Chapter(
                id="error_chapter",
                title="Error Chapter",
                description="An error occurred while generating the chapter.",
                events=[]
            )

class StoryManager:
    def __init__(self):
        self.chapter_generator = ChapterGenerator()
        self.pet = Pet(
            name="Luna",
            age=1,
            species="magical fox",
            emotional_state=EmotionalState([
                LatentVariable("happiness", 50),
                LatentVariable("excitement", 50),
                LatentVariable("calmness", 50),
                LatentVariable("curiosity", 70),
                LatentVariable("affection", 60)
            ]),
            physical_state=PhysicalState(
                variables=[
                    LatentVariable("energy", 80),
                    LatentVariable("health", 90),
                    LatentVariable("hunger", 30),
                    LatentVariable("cleanliness", 70)
                ],
                description=PhysicalDescription(
                    species="magical fox",
                    color="silver",
                    size="small",
                    distinctive_features=["glowing blue eyes", "shimmering fur"]
                )
            )
        )
        self.story_state = StoryState(
            current_chapter=None,
            player_attributes={"strength": 10, "intelligence": 10, "charisma": 10},
            world_state={"time": "dawn", "location": "enchanted forest"},
            inventory=["magic wand", "mysterious amulet"],
            pet=self.pet
        )
        self.story_context = {
            "genre": "magical adventure",
            "setting": "enchanted realm",
            "completed_chapters": []
        }

    def start_new_chapter(self):
        new_chapter = self.chapter_generator.generate_chapter(self.story_context)
        self.story_state.current_chapter = new_chapter
        self.story_context['completed_chapters'].append(new_chapter.id)
        print(f"Starting new chapter: {new_chapter.title}")
        print(new_chapter.description)

    def play_scene(self):
        scene = generate_dynamic_scene(self.story_state)
        print(scene.description)
        for i, choice in enumerate(scene.choices, 1):
            print(f"{i}. {choice['text']}")
        
        choice = int(input("Enter your choice: ")) - 1
        outcome = scene.choices[choice]['action']
        
        pet_reaction = self.pet.process_interaction(scene.choices[choice]['text'], self.story_state)
        
        self.story_state.current_chapter.add_to_narrative(scene.description, scene.choices[choice]['text'], outcome, pet_reaction)
        print(outcome)
        print(f"Pet reaction: {pet_reaction}")

        triggered_events = self.story_state.current_chapter.update(self.story_state)
        for event in triggered_events:
            print(f"Event triggered: {event.description}")

        if self.story_state.current_chapter.is_completed():
            print("Chapter completed!")
            return True
        return False

    def run_story(self):
        while True:
            if not self.story_state.current_chapter or self.story_state.current_chapter.is_completed():
                self.start_new_chapter()
            
            chapter_completed = self.play_scene()
            if chapter_completed:
                choice = input("Continue to next chapter? (y/n): ")
                if choice.lower() != 'y':
                    break

if __name__ == "__main__":
    story_manager = StoryManager()
    story_manager.run_story()