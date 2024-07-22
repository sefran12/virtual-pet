from dataclasses import dataclass
from typing import Callable

@dataclass
class ScenarioChoice:
    text: str
    action: Callable[['Game'], None]

    def execute(self, game: 'Game'):
        self.action(game)