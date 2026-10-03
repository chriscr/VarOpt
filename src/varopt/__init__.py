"""VarOpt: Domain-Agnostic Optimization Platform."""

from .core import (
    CandidateDecision,
    CallableEvaluation,
    Constraint,
    DecisionSpace,
    Evaluation,
    EvaluationResult,
    EvaluationStatus,
    Objective,
    ObjectiveSense,
    OptimizationProblem,
)

__version__ = "0.1.0"

__all__ = [
    "CandidateDecision",
    "CallableEvaluation",
    "Constraint",
    "DecisionSpace",
    "Evaluation",
    "EvaluationResult",
    "EvaluationStatus",
    "Objective",
    "ObjectiveSense",
    "OptimizationProblem",
]
