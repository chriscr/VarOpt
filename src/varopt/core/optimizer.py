"""Single-objective optimization for VarOpt."""

from collections.abc import Iterable
from enum import Enum

from .candidate import CandidateDecision
from .evaluation import Evaluation
from .evaluation_result import EvaluationResult, EvaluationStatus
from .objective import ObjectiveSense
from .problem import OptimizationProblem


class OptimizationStatus(Enum):
    """Outcome of an optimization attempt."""

    SUCCESS = "success"
    NO_ELIGIBLE_CANDIDATE = "no_eligible_candidate"


class OptimizationResult:
    """Result produced by the single-objective optimizer."""

    __slots__ = ("status", "best_candidate", "best_evaluation")

    def __init__(
        self,
        status: OptimizationStatus,
        best_candidate: CandidateDecision | None = None,
        best_evaluation: EvaluationResult | None = None,
    ) -> None:
        """Create an optimization result."""
        self.status = status
        self.best_candidate = best_candidate
        self.best_evaluation = best_evaluation

        if status is OptimizationStatus.SUCCESS:
            if best_candidate is None or best_evaluation is None:
                raise ValueError(
                    "A successful optimization result must contain "
                    "a candidate and evaluation."
                )
        elif status is OptimizationStatus.NO_ELIGIBLE_CANDIDATE:
            if best_candidate is not None or best_evaluation is not None:
                raise ValueError(
                    "A no-eligible-candidate result must not contain "
                    "a candidate or evaluation."
                )
        else:
            raise ValueError(f"Unsupported optimization status: {status!r}")


class Optimizer:
    """Deterministic single-objective optimizer over supplied candidates."""

    def __init__(self, evaluation: Evaluation) -> None:
        """Create an optimizer using the supplied evaluation mechanism."""
        self._evaluation = evaluation

    def optimize(
        self,
        problem: OptimizationProblem,
        candidates: Iterable[CandidateDecision],
    ) -> OptimizationResult:
        """Evaluate supplied candidates and retain the best eligible result."""
        if len(problem.objectives) != 1:
            raise ValueError(
                "The initial optimizer requires exactly one objective."
            )

        objective_sense = problem.objectives[0].sense

        best_candidate: CandidateDecision | None = None
        best_evaluation: EvaluationResult | None = None
        best_value = None

        for candidate in candidates:
            result = self._evaluation.evaluate(problem, candidate)

            if result.status is not EvaluationStatus.SUCCESS:
                continue

            if result.feasible is False:
                continue

            objective_value = result.objective_values[0]

            if best_evaluation is None:
                best_candidate = candidate
                best_evaluation = result
                best_value = objective_value
                continue

            if objective_sense is ObjectiveSense.MINIMIZE:
                if objective_value < best_value:
                    best_candidate = candidate
                    best_evaluation = result
                    best_value = objective_value
            elif objective_sense is ObjectiveSense.MAXIMIZE:
                if objective_value > best_value:
                    best_candidate = candidate
                    best_evaluation = result
                    best_value = objective_value
            else:
                raise ValueError(
                    f"Unsupported objective sense: {objective_sense!r}"
                )

        if best_evaluation is None:
            return OptimizationResult(
                status=OptimizationStatus.NO_ELIGIBLE_CANDIDATE,
            )

        return OptimizationResult(
            status=OptimizationStatus.SUCCESS,
            best_candidate=best_candidate,
            best_evaluation=best_evaluation,
        )