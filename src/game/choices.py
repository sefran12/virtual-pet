# src\game\choices.py
from dataclasses import dataclass
from typing import Callable

@dataclass
class ScenarioChoice:
    text: str
    action: Callable[['Game', str, str], None]

    def execute(self, game: 'Game', message: str, scenario: str):
        self.action(game, message, scenario)

@dataclass
class FreeformChoice:
    def execute(self, game: 'Game', message: str, scenario: str):
        game.process_freeform_action(message, scenario)