
"""Concrete deterministic beam-search experiment for Phase 4 architectural validation."""

from collections.abc import Callable, Iterable

from varopt.core.candidate import CandidateDecision
from varopt.core.evaluation import Evaluation
from varopt.core.objective import ObjectiveSense
from varopt.core.optimizer import (
    OptimizationResult,
    OptimizationStatus,
    Optimizer,
)
from varopt.core.problem import OptimizationProblem


class BeamSearchExperiment:
    """Concrete bounded beam-search architectural experiment.

    This is a non-public experiment, not a generalized search abstraction
    or public optimization strategy.
    """

    def __init__(
        self,
        evaluation: Evaluation,
        neighbor_function: Callable[
            [CandidateDecision], list[CandidateDecision]
        ],
        *,
        beam_width: int = 2,
        max_steps: int = 10,
    ) -> None:
        """Create a deterministic beam-search experiment."""
        if beam_width <= 0:
            raise ValueError("Beam width must be positive.")
        if max_steps <= 0:
            raise ValueError("Maximum steps must be positive.")

        self._optimizer = Optimizer(evaluation)
        self._neighbor_function = neighbor_function
        self._beam_width = beam_width
        self._max_steps = max_steps

    def optimize(
        self,
        problem: OptimizationProblem,
        initial_candidates: Iterable[CandidateDecision],
    ) -> OptimizationResult:
        """Search a bounded frontier and return the best eligible result."""
        if len(problem.objectives) != 1:
            raise ValueError(
                "The beam-search experiment requires exactly one objective."
            )

        objective_sense = problem.objectives[0].sense

        # Equality-based lists avoid requiring candidate values to be hashable.
        discovered: list[CandidateDecision] = []
        frontier: list[OptimizationResult] = []
        best_result: OptimizationResult | None = None

        # Evaluate initial candidates in their supplied order.
        for candidate in initial_candidates:
            if candidate in discovered:
                continue

            discovered.append(candidate)
            result = self._optimizer.optimize(problem, [candidate])

            if result.status is not OptimizationStatus.SUCCESS:
                continue

            best_result = self._retain_better(
                result,
                best_result,
                objective_sense,
            )
            frontier.append(result)

        frontier = self._rank_and_trim(frontier, objective_sense)

        # Expand the active frontier for a finite number of steps.
        for _ in range(self._max_steps):
            if not frontier:
                break

            next_frontier: list[OptimizationResult] = []

            # Frontier order and neighbor order define encounter order.
            for frontier_result in frontier:
                current_candidate = frontier_result.best_candidate

                if current_candidate is None:
                    raise RuntimeError(
                        "A successful optimization result must contain "
                        "a candidate."
                    )

                for neighbor in self._neighbor_function(current_candidate):
                    if neighbor in discovered:
                        continue

                    discovered.append(neighbor)
                    result = self._optimizer.optimize(problem, [neighbor])

                    if result.status is not OptimizationStatus.SUCCESS:
                        continue

                    best_result = self._retain_better(
                        result,
                        best_result,
                        objective_sense,
                    )
                    next_frontier.append(result)

            frontier = self._rank_and_trim(
                next_frontier,
                objective_sense,
            )

        if best_result is None:
            return OptimizationResult(
                status=OptimizationStatus.NO_ELIGIBLE_CANDIDATE,
            )

        return best_result

    @staticmethod
    def _objective_value(result: OptimizationResult):
        """Return the objective value from a successful result."""
        if result.best_evaluation is None:
            raise RuntimeError(
                "A successful optimization result must contain "
                "an evaluation."
            )

        return result.best_evaluation.objective_values[0]

    @classmethod
    def _retain_better(
        cls,
        candidate_result: OptimizationResult,
        best_result: OptimizationResult | None,
        objective_sense: ObjectiveSense,
    ) -> OptimizationResult:
        """Retain the better result, keeping the first result on a tie."""
        if best_result is None:
            return candidate_result

        candidate_value = cls._objective_value(candidate_result)
        best_value = cls._objective_value(best_result)

        if objective_sense is ObjectiveSense.MINIMIZE:
            if candidate_value < best_value:
                return candidate_result
        elif objective_sense is ObjectiveSense.MAXIMIZE:
            if candidate_value > best_value:
                return candidate_result
        else:
            raise ValueError(
                f"Unsupported objective sense: {objective_sense!r}"
            )

        return best_result

    def _rank_and_trim(
        self,
        results: list[OptimizationResult],
        objective_sense: ObjectiveSense,
    ) -> list[OptimizationResult]:
        """Rank eligible results and retain at most the configured width."""
        if objective_sense is ObjectiveSense.MINIMIZE:
            ranked = sorted(results, key=self._objective_value)
        elif objective_sense is ObjectiveSense.MAXIMIZE:
            ranked = sorted(
                results,
                key=self._objective_value,
                reverse=True,
            )
        else:
            raise ValueError(f"Unsupported objective sense: {objective_sense!r}")

        # Python's stable sorting preserves encounter order for equal values.
        return ranked[: self._beam_width]