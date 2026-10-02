"""VarOpt: Domain-Agnostic Optimization Platform."""

from .core import (
    CandidateDecision,
    Constraint,
    DecisionSpace,
    Objective,
    ObjectiveSense,
    OptimizationProblem,
)

__version__ = "0.1.0"

__all__ = [
    "CandidateDecision",
    "Constraint",
    "DecisionSpace",
    "Objective",
    "ObjectiveSense",
    "OptimizationProblem",
]
