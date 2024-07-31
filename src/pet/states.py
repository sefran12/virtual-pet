# src\pet\states.py
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class LatentVariable:
    name: str
    value: float

    def __post_init__(self):
        self.value = max(-100, min(100, self.value))  # Ensure value is between -100 and 100

@dataclass
class EmotionalState:
    variables: List[LatentVariable]

    def __post_init__(self):
        assert len(self.variables) == 5, "EmotionalState must have exactly 5 latent variables"

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

    def __post_init__(self):
        assert len(self.variables) == 4, "PhysicalState must have exactly 4 latent variables"

@dataclass
class EmotionalStateDelta:
    variable_deltas: Dict[str, float]

@dataclass
class PhysicalStateDelta:
    variable_deltas: Dict[str, float]