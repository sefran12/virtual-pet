# src/game/choices.py
from dataclasses import dataclass
from typing import Callable

@dataclass
class ScenarioChoice:
    text: str
    action: Callable[['Game', str], None]

    def execute(self, game: 'Game', message: str):
        self.action(game, message)

@dataclass
class FreeformChoice:
    def execute(self, game: 'Game', message: str):
        game.process_freeform_action(message)
