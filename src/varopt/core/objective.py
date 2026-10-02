"""Objective contract for VarOpt."""

from enum import Enum
from typing import Protocol


class ObjectiveSense(Enum):
    """Direction in which an objective is optimized."""

    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"


class Objective(Protocol):
    """Contract describing an optimization objective."""

    @property
    def name(self) -> str:
        """Return the objective name."""
        ...

    @property
    def sense(self) -> ObjectiveSense:
        """Return whether the objective is minimized or maximized."""
        ...
