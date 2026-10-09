
"""Concrete simulated-annealing experiment for Phase 4 architectural validation."""

from collections.abc import Callable
from math import exp
from random import Random

from varopt.core.candidate import CandidateDecision
from varopt.core.evaluation import Evaluation
from varopt.core.objective import ObjectiveSense
from varopt.core.optimizer import Optimizer, OptimizationResult
from varopt.core.problem import OptimizationProblem


class SimulatedAnnealingExperiment:
    """Concrete simulated-annealing experiment.

    This is an architectural validation experiment, not a generalized
    search abstraction or public optimization strategy.
    """

    def __init__(
        self,
        evaluation: Evaluation,
        neighbor_function: Callable[
            [CandidateDecision], list[CandidateDecision]
        ],
        *,
        seed: int,
        initial_temperature: float = 10.0,
        cooling_factor: float = 0.95,
        max_steps: int = 100,
    ) -> None:
        """Create a reproducible, bounded simulated-annealing experiment."""
        if initial_temperature <= 0:
            raise ValueError("Initial temperature must be positive.")
        if not 0 < cooling_factor < 1:
            raise ValueError("Cooling factor must be between 0 and 1.")
        if max_steps <= 0:
            raise ValueError("Maximum steps must be positive.")

        self._optimizer = Optimizer(evaluation)
        self._neighbor_function = neighbor_function
        self._random = Random(seed)
        self._initial_temperature = initial_temperature
        self._cooling_factor = cooling_factor
        self._max_steps = max_steps

    def optimize(
        self,
        problem: OptimizationProblem,
        initial_candidate: CandidateDecision,
    ) -> OptimizationResult:
        """Run simulated annealing and return the best eligible result."""
        if len(problem.objectives) != 1:
            raise ValueError(
                "The simulated-annealing experiment requires "
                "exactly one objective."
            )

        objective_sense = problem.objectives[0].sense

        current_candidate = initial_candidate
        current_result = self._optimizer.optimize(
            problem,
            [current_candidate],
        )

        if current_result.best_candidate is None:
            return current_result

        best_result = current_result

        for step in range(self._max_steps):
            neighbors = self._neighbor_function(current_candidate)

            if not neighbors:
                break

            neighbor = self._random.choice(neighbors)
            neighbor_result = self._optimizer.optimize(problem, [neighbor])

            temperature = (
                self._initial_temperature
                * self._cooling_factor**step
            )

            if neighbor_result.best_candidate is None:
                continue

            current_evaluation = current_result.best_evaluation
            neighbor_evaluation = neighbor_result.best_evaluation

            if current_evaluation is None or neighbor_evaluation is None:
                raise RuntimeError(
                    "Successful optimization results must contain "
                    "an evaluation."
                )

            current_value = current_evaluation.objective_values[0]
            neighbor_value = neighbor_evaluation.objective_values[0]

            if objective_sense is ObjectiveSense.MINIMIZE:
                delta = neighbor_value - current_value
            elif objective_sense is ObjectiveSense.MAXIMIZE:
                delta = current_value - neighbor_value
            else:
                raise ValueError(
                    f"Unsupported objective sense: {objective_sense!r}"
                )

            if delta < 0:
                accepted = True
            elif delta == 0:
                accepted = False
            else:
                acceptance_probability = exp(-delta / temperature)
                accepted = (
                    self._random.random() < acceptance_probability
                )

            if accepted:
                current_candidate = neighbor
                current_result = neighbor_result

            best_evaluation = best_result.best_evaluation
            if best_evaluation is None:
                raise RuntimeError(
                    "Successful optimization results must contain "
                    "an evaluation."
                )

            best_value = best_evaluation.objective_values[0]

            if objective_sense is ObjectiveSense.MINIMIZE:
                improves_best = neighbor_value < best_value
            else:
                improves_best = neighbor_value > best_value

            if improves_best:
                best_result = neighbor_result

        return best_result