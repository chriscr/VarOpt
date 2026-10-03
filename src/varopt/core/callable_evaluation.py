"""Callable-based deterministic evaluation for VarOpt."""

from collections.abc import Callable, Sequence
from typing import Any

from .candidate import CandidateDecision
from .evaluation_result import EvaluationResult, EvaluationStatus
from .problem import OptimizationProblem


class CallableEvaluation:
    """Deterministic evaluation using supplied objective callables.

    Objective definitions remain separate from the mechanisms that calculate
    their values. Constraints use the existing Constraint contract.
    """

    def __init__(
        self,
        objective_functions: Sequence[
            Callable[[CandidateDecision], Any]
        ] = (),
    ) -> None:
        """Create an evaluation mechanism with objective value functions."""
        self._objective_functions = tuple(objective_functions)

    def evaluate(
        self,
        problem: OptimizationProblem,
        candidate: CandidateDecision,
    ) -> EvaluationResult:
        """Evaluate a candidate and return its semantic result."""
        if len(self._objective_functions) != len(problem.objectives):
            return EvaluationResult(
                candidate=candidate,
                status=EvaluationStatus.FAILED,
                feasible=None,
            )

        try:
            objective_values = tuple(
                objective_function(candidate)
                for objective_function in self._objective_functions
            )

            constraint_results = tuple(
                constraint.is_satisfied(candidate)
                for constraint in problem.constraints
            )
        except Exception:
            return EvaluationResult(
                candidate=candidate,
                status=EvaluationStatus.FAILED,
                feasible=None,
            )

        if constraint_results:
            feasible: bool | None = all(constraint_results)
        else:
            feasible = None

        return EvaluationResult(
            candidate=candidate,
            status=EvaluationStatus.SUCCESS,
            feasible=feasible,
            objective_values=objective_values,
            constraint_results=constraint_results,
        )