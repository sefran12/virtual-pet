# src\game\choices.py
from dataclasses import dataclass
from typing import Callable

@dataclass
class ScenarioChoice:
    text: str
    action: Callable

    def execute(self, game: 'Game', message: str, scenario: str):
        # Call action with the correct number of arguments based on its signature
        import inspect
        sig = inspect.signature(self.action)
        if len(sig.parameters) == 4:  # For lambda with action_text
            self.action(game, message, scenario, self.text)
        else:  # For standard actions
            self.action(game, message, scenario)

@dataclass
class FreeformChoice:
    def execute(self, game: 'Game', message: str, scenario: str):
        game.process_freeform_action(message, scenario)
