"""Optimization problem representation."""

from dataclasses import dataclass

from .constraint import Constraint
from .decision_space import DecisionSpace
from .objective import Objective


@dataclass(frozen=True, slots=True)
class OptimizationProblem:
    """Minimal domain-neutral optimization problem definition."""

    decision_space: DecisionSpace
    objectives: tuple[Objective, ...] = ()
    constraints: tuple[Constraint, ...] = ()
