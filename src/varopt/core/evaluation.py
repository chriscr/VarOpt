"""Evaluation boundary for VarOpt."""

from typing import Protocol

from .candidate import CandidateDecision
from .evaluation_result import EvaluationResult
from .problem import OptimizationProblem


class Evaluation(Protocol):
    """Contract for a replaceable evaluation mechanism."""

    def evaluate(
        self,
        problem: OptimizationProblem,
        candidate: CandidateDecision,
    ) -> EvaluationResult:
        """Evaluate a candidate within an optimization problem."""
        ...
