
from math import isclose

import pytest

from varopt import (
    CandidateDecision,
    EvaluationResult,
    EvaluationStatus,
    ObjectiveSense,
    OptimizationProblem,
    OptimizationStatus,
)
from varopt.experiments.simulated_annealing_experiment import (
    SimulatedAnnealingExperiment,
)


class SimpleDecisionSpace:
    """Test-only decision space for integer candidates."""

    def is_representable(self, candidate: CandidateDecision) -> bool:
        return isinstance(candidate.value, int) and 0 <= candidate.value <= 10


class TwoWellMinimizeObjective:
    """Test-only two-well minimization objective."""

    @property
    def name(self) -> str:
        return "two_well"

    @property
    def sense(self) -> ObjectiveSense:
        return ObjectiveSense.MINIMIZE


class StubEvaluation:
    """Test-only deterministic evaluation."""

    def __init__(self, objective_function):
        self._objective_function = objective_function

    def evaluate(
        self,
        problem: OptimizationProblem,
        candidate: CandidateDecision,
    ) -> EvaluationResult:
        return EvaluationResult(
            candidate=candidate,
            status=EvaluationStatus.SUCCESS,
            feasible=True,
            objective_values=(self._objective_function(candidate.value),),
            constraint_results=(),
        )


def two_well_value(x: int) -> float:
    """Return the deterministic two-well objective value."""
    return min((x - 2) ** 2, (x - 8) ** 2 + 2)


def neighbor_function(candidate: CandidateDecision) -> list[CandidateDecision]:
    """Return bounded adjacent integer candidates in deterministic order."""
    x = candidate.value
    neighbors = []

    if x > 0:
        neighbors.append(CandidateDecision(x - 1))

    if x < 10:
        neighbors.append(CandidateDecision(x + 1))

    return neighbors


def make_problem() -> OptimizationProblem:
    """Create the concrete two-well minimization problem."""
    return OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(TwoWellMinimizeObjective(),),
        constraints=(),
    )


def make_experiment(
    *,
    seed: int = 42,
    initial_temperature: float = 10.0,
    cooling_factor: float = 0.95,
    max_steps: int = 100,
    objective_function=two_well_value,
    neighbors=neighbor_function,
) -> SimulatedAnnealingExperiment:
    """Create a concrete simulated-annealing experiment."""
    return SimulatedAnnealingExperiment(
        evaluation=StubEvaluation(objective_function),
        neighbor_function=neighbors,
        seed=seed,
        initial_temperature=initial_temperature,
        cooling_factor=cooling_factor,
        max_steps=max_steps,
    )


def test_simulated_annealing_returns_best_candidate_seen() -> None:
    """The result retains the best candidate, not merely the final state."""
    experiment = make_experiment()
    result = experiment.optimize(make_problem(), CandidateDecision(8))

    assert result.status is OptimizationStatus.SUCCESS
    assert result.best_candidate is not None
    assert result.best_candidate.value == 2
    assert result.best_evaluation is not None
    assert result.best_evaluation.objective_values == (0,)


def test_simulated_annealing_is_reproducible_for_same_seed() -> None:
    """Fresh experiments with identical inputs produce identical results."""
    first = make_experiment(seed=123).optimize(
        make_problem(), CandidateDecision(8)
    )
    second = make_experiment(seed=123).optimize(
        make_problem(), CandidateDecision(8)
    )

    assert first.status is second.status
    assert first.best_candidate is not None
    assert second.best_candidate is not None
    assert first.best_candidate.value == second.best_candidate.value
    assert first.best_evaluation is not None
    assert second.best_evaluation is not None
    assert (
        first.best_evaluation.objective_values
        == second.best_evaluation.objective_values
    )


def test_simulated_annealing_can_accept_a_worsening_move() -> None:
    """A high temperature can allow a worse candidate to become current."""
    visited = []

    def controlled_neighbors(candidate: CandidateDecision):
        visited.append(candidate.value)
        if len(visited) == 1:
            return [CandidateDecision(9)]
        return []

    experiment = make_experiment(
        seed=42,
        initial_temperature=100.0,
        max_steps=2,
        neighbors=controlled_neighbors,
    )

    result = experiment.optimize(make_problem(), CandidateDecision(8))

    assert visited == [8, 9]
    assert result.status is OptimizationStatus.SUCCESS
    assert result.best_candidate is not None
    assert result.best_candidate.value == 8


def test_simulated_annealing_can_reject_a_worsening_move() -> None:
    """A sufficiently low temperature rejects a worse candidate."""
    visited = []

    def controlled_neighbors(candidate: CandidateDecision):
        visited.append(candidate.value)
        if len(visited) == 1:
            return [CandidateDecision(9)]
        return []

    experiment = make_experiment(
        seed=42,
        initial_temperature=0.01,
        max_steps=2,
        neighbors=controlled_neighbors,
    )

    result = experiment.optimize(make_problem(), CandidateDecision(8))

    assert visited == [8, 8]
    assert result.status is OptimizationStatus.SUCCESS
    assert result.best_candidate is not None
    assert result.best_candidate.value == 8


def test_simulated_annealing_terminates_when_there_are_no_neighbors() -> None:
    """An empty neighborhood ends the run with its best eligible result."""
    experiment = make_experiment(neighbors=lambda candidate: [])

    result = experiment.optimize(make_problem(), CandidateDecision(8))

    assert result.status is OptimizationStatus.SUCCESS
    assert result.best_candidate is not None
    assert result.best_candidate.value == 8


def test_simulated_annealing_returns_no_eligible_for_ineligible_initial() -> None:
    """An ineligible initial candidate produces no eligible result."""
    class IneligibleEvaluation:
        def evaluate(self, problem, candidate):
            return EvaluationResult(
                candidate=candidate,
                status=EvaluationStatus.SUCCESS,
                feasible=False,
                objective_values=(two_well_value(candidate.value),),
                constraint_results=(),
            )

    experiment = SimulatedAnnealingExperiment(
        evaluation=IneligibleEvaluation(),
        neighbor_function=neighbor_function,
        seed=42,
        max_steps=5,
    )

    result = experiment.optimize(make_problem(), CandidateDecision(8))

    assert result.status is OptimizationStatus.NO_ELIGIBLE_CANDIDATE
    assert result.best_candidate is None
    assert result.best_evaluation is None


def test_simulated_annealing_rejects_invalid_configuration() -> None:
    """Invalid temperature, cooling factor, and step count are rejected."""
    evaluation = StubEvaluation(two_well_value)

    with pytest.raises(ValueError, match="Initial temperature"):
        SimulatedAnnealingExperiment(
            evaluation, neighbor_function, seed=1, initial_temperature=0
        )

    with pytest.raises(ValueError, match="Cooling factor"):
        SimulatedAnnealingExperiment(
            evaluation, neighbor_function, seed=1, cooling_factor=1
        )

    with pytest.raises(ValueError, match="Maximum steps"):
        SimulatedAnnealingExperiment(
            evaluation, neighbor_function, seed=1, max_steps=0
        )


def test_simulated_annealing_rejects_multiple_objectives() -> None:
    """The experiment supports exactly one objective."""
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(
            TwoWellMinimizeObjective(),
            TwoWellMinimizeObjective(),
        ),
        constraints=(),
    )

    experiment = make_experiment()

    with pytest.raises(ValueError, match="exactly one objective"):
        experiment.optimize(problem, CandidateDecision(8))
        

def test_simulated_annealing_uses_maximize_objective_sense() -> None:
    """Higher objective values are treated as improvements for MAXIMIZE."""
    class SimpleMaximizeObjective:
        @property
        def name(self) -> str:
            return "value"

        @property
        def sense(self) -> ObjectiveSense:
            return ObjectiveSense.MAXIMIZE

    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(SimpleMaximizeObjective(),),
        constraints=(),
    )

    def value(x: int) -> float:
        return float(x)

    experiment = make_experiment(
        objective_function=value,
        neighbors=lambda candidate: (
            [CandidateDecision(candidate.value + 1)]
            if candidate.value < 10
            else []
        ),
        max_steps=3,
    )

    result = experiment.optimize(problem, CandidateDecision(5))

    assert result.status is OptimizationStatus.SUCCESS
    assert result.best_candidate is not None
    assert result.best_candidate.value == 8
    assert result.best_evaluation is not None
    assert result.best_evaluation.objective_values == (8.0,)


def test_simulated_annealing_honors_step_limit() -> None:
    """The experiment requests no more than max_steps neighborhoods."""
    visited = []

    def controlled_neighbors(candidate: CandidateDecision):
        visited.append(candidate.value)
        return [CandidateDecision(candidate.value + 1)]

    experiment = make_experiment(
        neighbors=controlled_neighbors,
        max_steps=3,
    )

    result = experiment.optimize(make_problem(), CandidateDecision(5))

    assert len(visited) == 3
    assert result.status is OptimizationStatus.SUCCESS
    assert result.best_candidate is not None
    assert result.best_candidate.value == 8


def test_simulated_annealing_continues_after_failed_neighbor_evaluation() -> None:
    """A failed neighbor is skipped and a later candidate can be accepted."""
    visited = []

    class FailAtSixEvaluation:
        def evaluate(
            self,
            problem: OptimizationProblem,
            candidate: CandidateDecision,
        ) -> EvaluationResult:
            if candidate.value == 6:
                return EvaluationResult(
                    candidate=candidate,
                    status=EvaluationStatus.FAILED,
                    feasible=None,
                    objective_values=(),
                    constraint_results=(),
                )

            return EvaluationResult(
                candidate=candidate,
                status=EvaluationStatus.SUCCESS,
                feasible=True,
                objective_values=(two_well_value(candidate.value),),
                constraint_results=(),
            )

    def controlled_neighbors(candidate: CandidateDecision):
        visited.append(candidate.value)

        if candidate.value == 5 and len(visited) == 1:
            return [CandidateDecision(6)]

        if candidate.value == 5 and len(visited) == 2:
            return [CandidateDecision(7)]

        return []

    experiment = SimulatedAnnealingExperiment(
        evaluation=FailAtSixEvaluation(),
        neighbor_function=controlled_neighbors,
        seed=42,
        max_steps=3,
    )

    result = experiment.optimize(make_problem(), CandidateDecision(5))

    assert visited == [5, 5, 7]
    assert result.status is OptimizationStatus.SUCCESS
    assert result.best_candidate is not None
    assert result.best_candidate.value == 7
    assert result.best_evaluation is not None
    assert result.best_evaluation.objective_values == (3,)