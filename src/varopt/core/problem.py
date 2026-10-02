"""Optimization problem representation."""

from dataclasses import dataclass

from .decision_space import DecisionSpace


@dataclass(frozen=True, slots=True)
class OptimizationProblem:
    """Minimal domain-neutral optimization problem definition."""

    decision_space: DecisionSpace