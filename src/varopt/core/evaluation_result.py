"""Evaluation result value object for VarOpt."""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .candidate import CandidateDecision


class EvaluationStatus(Enum):
    """Outcome of an evaluation attempt."""

    SUCCESS = "success"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    """Semantic result produced by evaluating a candidate."""

    candidate: CandidateDecision
    status: EvaluationStatus
    feasible: bool | None
    objective_values: tuple[Any, ...] = ()
    constraint_results: tuple[bool | None, ...] = ()

    def __post_init__(self) -> None:
        """Enforce the distinction between evaluation failure and infeasibility."""
        if self.status is EvaluationStatus.FAILED and self.feasible is not None:
            raise ValueError(
                "A failed evaluation must not establish feasibility."
            )
