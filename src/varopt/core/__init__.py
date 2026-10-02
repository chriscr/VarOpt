"""Core VarOpt abstractions."""

from .candidate import CandidateDecision
from .decision_space import DecisionSpace
from .problem import OptimizationProblem

__all__ = [
    "CandidateDecision",
    "DecisionSpace",
    "OptimizationProblem",
]