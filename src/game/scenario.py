from dataclasses import dataclass, field
from typing import List, Optional, Callable
from .choices import ScenarioChoice
import json

@dataclass
class Scenario:
    id: str
    description: str
    choices: List[ScenarioChoice]
    auto_update: Optional[Callable[['Game'], None]] = None

    @classmethod
    def from_dict(cls, data: dict, choice_actions: dict):
        choices = [
            ScenarioChoice(choice['text'], choice_actions[choice['action']])
            for choice in data['choices']
        ]
        return cls(
            id=data['id'],
            description=data['description'],
            choices=choices,
            auto_update=choice_actions.get(data.get('auto_update'))
        )

    @classmethod
    def load_scenarios(cls, file_path: str, choice_actions: dict) -> List['Scenario']:
        with open(file_path, 'r') as f:
            scenarios_data = json.load(f)
        return [cls.from_dict(scenario_data, choice_actions) for scenario_data in scenarios_data]