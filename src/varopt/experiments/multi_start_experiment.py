"""Concrete deterministic multi-start experiment for Phase 4 architectural validation."""

from collections.abc import Iterable

from varopt.core.candidate import CandidateDecision
from varopt.core.objective import ObjectiveSense
from varopt.core.optimizer import OptimizationResult, OptimizationStatus
from varopt.core.problem import OptimizationProblem
from varopt.experiments.hill_climbing_experiment import HillClimbingExperiment


class MultiStartExperiment:
    """Deterministic multi-start local-search experiment.

    This is a concrete architectural validation experiment. It is not a
    generalized multi-start search abstraction or public optimization strategy.
    """

    def __init__(
        self,
        hill_climbing: HillClimbingExperiment,
    ) -> None:
        """Create a multi-start experiment using the supplied local search."""
        self._hill_climbing = hill_climbing

    def optimize(
        self,
        problem: OptimizationProblem,
        initial_candidates: Iterable[CandidateDecision],
    ) -> OptimizationResult:
        """Run independent local searches and retain the best result."""
        if len(problem.objectives) != 1:
            raise ValueError(
                "The multi-start experiment requires exactly one objective."
            )

        objective_sense = problem.objectives[0].sense

        best_result: OptimizationResult | None = None

        for initial_candidate in initial_candidates:
            local_result = self._hill_climbing.optimize(
                problem,
                initial_candidate,
            )

            if local_result.status is not OptimizationStatus.SUCCESS:
                continue

            if local_result.best_evaluation is None:
                raise RuntimeError(
                    "A successful optimization result must contain "
                    "an evaluation."
                )

            if best_result is None:
                best_result = local_result
                continue

            if best_result.best_evaluation is None:
                raise RuntimeError(
                    "A successful optimization result must contain "
                    "an evaluation."
                )

            local_value = local_result.best_evaluation.objective_values[0]
            best_value = best_result.best_evaluation.objective_values[0]

            if objective_sense is ObjectiveSense.MINIMIZE:
                if local_value < best_value:
                    best_result = local_result
            elif objective_sense is ObjectiveSense.MAXIMIZE:
                if local_value > best_value:
                    best_result = local_result
            else:
                raise ValueError(
                    f"Unsupported objective sense: {objective_sense!r}"
                )

        if best_result is None:
            return OptimizationResult(
                status=OptimizationStatus.NO_ELIGIBLE_CANDIDATE,
            )

        return best_result