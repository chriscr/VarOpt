"""Concrete hill-climbing experiment for Phase 4 architectural validation."""

from collections.abc import Callable

from varopt.core.candidate import CandidateDecision
from varopt.core.evaluation import Evaluation
from varopt.core.optimizer import Optimizer, OptimizationResult
from varopt.core.objective import ObjectiveSense
from varopt.core.problem import OptimizationProblem


class HillClimbingExperiment:
    """Deterministic strict-improvement hill-climbing experiment.

    This is a concrete architectural validation experiment. It is not a
    generalized search abstraction or public optimization strategy.
    """

    def __init__(
        self,
        evaluation: Evaluation,
        neighbor_function: Callable[
            [CandidateDecision], list[CandidateDecision]
        ],
    ) -> None:
        """Create a hill-climbing experiment."""
        self._optimizer = Optimizer(evaluation)
        self._neighbor_function = neighbor_function

    def optimize(
        self,
        problem: OptimizationProblem,
        initial_candidate: CandidateDecision,
    ) -> OptimizationResult:
        """Run deterministic strict-improvement hill climbing."""
        if len(problem.objectives) != 1:
            raise ValueError(
                "The hill-climbing experiment requires exactly one objective."
            )

        objective_sense = problem.objectives[0].sense

        current_candidate = initial_candidate
        current_result = self._optimizer.optimize(
            problem,
            [current_candidate],
        )

        if current_result.best_candidate is None:
            return current_result

        while True:
            neighbors = self._neighbor_function(current_candidate)

            local_candidates = [current_candidate, *neighbors]

            local_result = self._optimizer.optimize(
                problem,
                local_candidates,
            )

            if local_result.best_candidate is None:
                return current_result

            current_evaluation = current_result.best_evaluation
            local_evaluation = local_result.best_evaluation

            if current_evaluation is None or local_evaluation is None:
                raise RuntimeError(
                    "Successful optimization results must contain "
                    "an evaluation."
                )

            current_value = current_evaluation.objective_values[0]
            local_value = local_evaluation.objective_values[0]

            if objective_sense is ObjectiveSense.MINIMIZE:
                strictly_better = local_value < current_value
            elif objective_sense is ObjectiveSense.MAXIMIZE:
                strictly_better = local_value > current_value
            else:
                raise ValueError(
                    f"Unsupported objective sense: {objective_sense!r}"
                )

            if not strictly_better:
                return current_result

            current_candidate = local_result.best_candidate
            current_result = local_result