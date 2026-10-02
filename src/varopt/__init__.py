"""VarOpt: Domain-Agnostic Optimization Platform."""

from .core import CandidateDecision, DecisionSpace, OptimizationProblem

__version__ = "0.1.0"

__all__ = [
    "CandidateDecision",
    "DecisionSpace",
    "OptimizationProblem",
]