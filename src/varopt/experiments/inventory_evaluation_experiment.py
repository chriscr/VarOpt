"""Concrete deterministic inventory evaluation experiment for Phase 5."""

from dataclasses import dataclass
import math
from numbers import Real
from typing import Any

from varopt.core.candidate import CandidateDecision
from varopt.core.evaluation_result import EvaluationResult, EvaluationStatus
from varopt.core.problem import OptimizationProblem


def _is_nonnegative_integer(value: Any) -> bool:
    """Return whether value is a nonnegative integer but not a boolean."""
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _is_finite_nonnegative_number(value: Any) -> bool:
    """Return whether value is a finite, nonnegative real number."""
    if isinstance(value, bool) or not isinstance(value, Real) or value < 0:
        return False
    try:
        return math.isfinite(value)
    except (OverflowError, TypeError, ValueError):
        return False


@dataclass(frozen=True, slots=True)
class InventoryContext:
    """Immutable inputs shared by evaluations of the inventory model.

    Demand and inventory quantities are nonnegative integers. Cost coefficients
    may be nonnegative finite integers or floating-point values.
    """

    initial_inventory: int
    demand: tuple[int, ...]
    production_cost: Real
    holding_cost: Real
    shortage_penalty: Real

    def __post_init__(self) -> None:
        """Reject invalid context at construction time."""
        if not _is_nonnegative_integer(self.initial_inventory):
            raise ValueError("Initial inventory must be a nonnegative integer.")
        if not isinstance(self.demand, tuple) or not self.demand:
            raise ValueError("Demand must be a nonempty tuple of nonnegative integers.")
        if not all(_is_nonnegative_integer(value) for value in self.demand):
            raise ValueError("Demand must contain only nonnegative integers.")

        for name, value in (
            ("Production cost", self.production_cost),
            ("Holding cost", self.holding_cost),
            ("Shortage penalty", self.shortage_penalty),
        ):
            if not _is_finite_nonnegative_number(value):
                raise ValueError(f"{name} must be a finite nonnegative number.")


class InventoryDecisionSpace:
    """Concrete decision space for fixed-horizon production plans."""

    __slots__ = ("_horizon",)

    def __init__(self, horizon: int) -> None:
        if not _is_nonnegative_integer(horizon) or horizon == 0:
            raise ValueError("Horizon must be a positive integer.")
        self._horizon = horizon

    def is_representable(self, candidate: CandidateDecision) -> bool:
        """Accept only horizon-length tuples of nonnegative integer quantities."""
        plan = candidate.value
        return (
            isinstance(plan, tuple)
            and len(plan) == self._horizon
            and all(_is_nonnegative_integer(quantity) for quantity in plan)
        )


class InventoryEvaluationExperiment:
    """Evaluate a production plan using deterministic inventory dynamics.

    The fixed context belongs to this evaluator instance. Inventory state is
    local to each call and is never stored on the evaluator or candidate.
    Shortage incurs an objective penalty; it is not a constraint violation.
    """

    __slots__ = ("_context",)

    def __init__(self, context: InventoryContext) -> None:
        self._context = context

    def evaluate(
        self,
        problem: OptimizationProblem,
        candidate: CandidateDecision,
    ) -> EvaluationResult:
        """Return the total cost or a failed result for invalid evaluation input."""
        if len(problem.objectives) != 1 or problem.constraints:
            return self._failed(candidate)
        try:
            if not problem.decision_space.is_representable(candidate):
                return self._failed(candidate)
        except Exception:
            return self._failed(candidate)

        plan = candidate.value
        if not self._is_valid_plan(plan):
            return self._failed(candidate)

        inventory = self._context.initial_inventory
        total_cost: int | float = 0

        try:
            for production, demand in zip(plan, self._context.demand):
                available = inventory + production
                shortage = max(0, demand - available)
                ending_inventory = max(0, available - demand)

                total_cost += (
                    self._context.production_cost * production
                    + self._context.holding_cost * ending_inventory
                    + self._context.shortage_penalty * shortage
                )
                inventory = ending_inventory
        except Exception:
            return self._failed(candidate)

        if isinstance(total_cost, float) and not math.isfinite(total_cost):
            return self._failed(candidate)

        return EvaluationResult(
            candidate=candidate,
            status=EvaluationStatus.SUCCESS,
            feasible=None,
            objective_values=(total_cost,),
            constraint_results=(),
        )

    def _is_valid_plan(self, plan: Any) -> bool:
        return (
            isinstance(plan, tuple)
            and len(plan) == len(self._context.demand)
            and all(_is_nonnegative_integer(quantity) for quantity in plan)
        )

    @staticmethod
    def _failed(candidate: CandidateDecision) -> EvaluationResult:
        return EvaluationResult(
            candidate=candidate,
            status=EvaluationStatus.FAILED,
            feasible=None,
        )
