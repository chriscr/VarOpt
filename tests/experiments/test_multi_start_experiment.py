from varopt import (
    CandidateDecision,
    EvaluationResult,
    EvaluationStatus,
    ObjectiveSense,
    OptimizationProblem,
    OptimizationResult,
    OptimizationStatus,
)
from varopt.experiments.hill_climbing_experiment import HillClimbingExperiment
from varopt.experiments.multi_start_experiment import MultiStartExperiment


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
        value = self._objective_function(candidate.value)

        return EvaluationResult(
            candidate=candidate,
            status=EvaluationStatus.SUCCESS,
            feasible=True,
            objective_values=(value,),
            constraint_results=(),
        )

class StubHillClimbing:
    """Test-only local-search stub returning predetermined results."""

    def __init__(self, results):
        self._results = iter(results)

    def optimize(
        self,
        problem: OptimizationProblem,
        initial_candidate: CandidateDecision,
    ) -> OptimizationResult:
        return next(self._results)

def two_well_value(x: int) -> float:
    """Return the deterministic two-well objective value."""
    return min((x - 2) ** 2, (x - 8) ** 2 + 2)


def neighbor_function(candidate: CandidateDecision) -> list[CandidateDecision]:
    """Return bounded adjacent integer candidates."""
    x = candidate.value
    neighbors = []

    if x > 0:
        neighbors.append(CandidateDecision(x - 1))

    if x < 10:
        neighbors.append(CandidateDecision(x + 1))

    return neighbors


def make_problem() -> OptimizationProblem:
    """Create the concrete Experiment 2 optimization problem."""
    return OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(TwoWellMinimizeObjective(),),
        constraints=(),
    )


def make_experiment() -> MultiStartExperiment:
    """Create the concrete multi-start experiment."""
    evaluation = StubEvaluation(two_well_value)

    hill_climbing = HillClimbingExperiment(
        evaluation=evaluation,
        neighbor_function=neighbor_function,
    )

    return MultiStartExperiment(hill_climbing=hill_climbing)


def test_multi_start_selects_best_local_optimum() -> None:
    """Select the best result from independent local-search trajectories."""
    experiment = make_experiment()
    problem = make_problem()

    result = experiment.optimize(
        problem,
        [
            CandidateDecision(2),
            CandidateDecision(8),
        ],
    )

    assert result.status is OptimizationStatus.SUCCESS
    assert result.best_candidate is not None
    assert result.best_candidate.value == 2
    assert result.best_evaluation is not None
    assert result.best_evaluation.objective_values == (0,)


def test_multi_start_with_one_start_matches_local_search() -> None:
    """A single starting point produces that local search's result."""
    experiment = make_experiment()
    problem = make_problem()

    result = experiment.optimize(
        problem,
        [CandidateDecision(8)],
    )

    assert result.status is OptimizationStatus.SUCCESS
    assert result.best_candidate is not None
    assert result.best_candidate.value == 8
    assert result.best_evaluation is not None
    assert result.best_evaluation.objective_values == (2,)


def test_multi_start_equal_results_retain_first() -> None:
    """Equal objective values retain the first encountered result."""
    experiment = make_experiment()
    problem = make_problem()

    result = experiment.optimize(
        problem,
        [
            CandidateDecision(2),
            CandidateDecision(2),
        ],
    )

    assert result.status is OptimizationStatus.SUCCESS
    assert result.best_candidate is not None
    assert result.best_candidate is not None
    assert result.best_candidate.value == 2


def test_multi_start_rejects_multiple_objectives() -> None:
    """The initial multi-start experiment supports exactly one objective."""
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(
            TwoWellMinimizeObjective(),
            TwoWellMinimizeObjective(),
        ),
        constraints=(),
    )

    experiment = make_experiment()

    try:
        experiment.optimize(
            problem,
            [CandidateDecision(2)],
        )
    except ValueError as exc:
        assert str(exc) == (
            "The multi-start experiment requires exactly one objective."
        )
    else:
        raise AssertionError("Expected ValueError for multiple objectives.")


def test_multi_start_skips_ineligible_local_search_results() -> None:
    """An ineligible local search does not prevent later results."""
    problem = make_problem()

    ineligible_result = OptimizationResult(
        status=OptimizationStatus.NO_ELIGIBLE_CANDIDATE,
    )

    successful_result = OptimizationResult(
        status=OptimizationStatus.SUCCESS,
        best_candidate=CandidateDecision(2),
        best_evaluation=EvaluationResult(
            candidate=CandidateDecision(2),
            status=EvaluationStatus.SUCCESS,
            feasible=True,
            objective_values=(0,),
            constraint_results=(),
        ),
    )

    experiment = MultiStartExperiment(
        hill_climbing=StubHillClimbing(
            [ineligible_result, successful_result]
        )
    )

    result = experiment.optimize(
        problem,
        [
            CandidateDecision(8),
            CandidateDecision(2),
        ],
    )

    assert result.status is OptimizationStatus.SUCCESS
    assert result.best_candidate is not None
    assert result.best_candidate.value == 2


def test_multi_start_returns_no_eligible_when_all_local_searches_are_ineligible() -> None:
    """All ineligible local searches produce no eligible overall result."""
    problem = make_problem()

    ineligible_result = OptimizationResult(
        status=OptimizationStatus.NO_ELIGIBLE_CANDIDATE,
    )

    experiment = MultiStartExperiment(
        hill_climbing=StubHillClimbing(
            [ineligible_result, ineligible_result]
        )
    )

    result = experiment.optimize(
        problem,
        [
            CandidateDecision(2),
            CandidateDecision(8),
        ],
    )

    assert result.status is OptimizationStatus.NO_ELIGIBLE_CANDIDATE
    assert result.best_candidate is None
    assert result.best_evaluation is None


def test_multi_start_uses_maximize_objective_sense() -> None:
    """Global comparison follows MAXIMIZE objective sense."""
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

    result_a = OptimizationResult(
        status=OptimizationStatus.SUCCESS,
        best_candidate=CandidateDecision(2),
        best_evaluation=EvaluationResult(
            candidate=CandidateDecision(2),
            status=EvaluationStatus.SUCCESS,
            feasible=True,
            objective_values=(10,),
            constraint_results=(),
        ),
    )

    result_b = OptimizationResult(
        status=OptimizationStatus.SUCCESS,
        best_candidate=CandidateDecision(8),
        best_evaluation=EvaluationResult(
            candidate=CandidateDecision(8),
            status=EvaluationStatus.SUCCESS,
            feasible=True,
            objective_values=(20,),
            constraint_results=(),
        ),
    )

    experiment = MultiStartExperiment(
        hill_climbing=StubHillClimbing([result_a, result_b])
    )

    result = experiment.optimize(
        problem,
        [
            CandidateDecision(2),
            CandidateDecision(8),
        ],
    )

    assert result.status is OptimizationStatus.SUCCESS
    assert result.best_candidate is not None
    assert result.best_candidate.value == 8


def test_multi_start_does_not_evaluate_candidates_directly() -> None:
    """Multi-start delegates local-search execution to its supplied component."""
    class RecordingHillClimbing:
        def __init__(self):
            self.calls = []

        def optimize(
            self,
            problem: OptimizationProblem,
            initial_candidate: CandidateDecision,
        ) -> OptimizationResult:
            self.calls.append(initial_candidate)
            return OptimizationResult(
                status=OptimizationStatus.SUCCESS,
                best_candidate=initial_candidate,
                best_evaluation=EvaluationResult(
                    candidate=initial_candidate,
                    status=EvaluationStatus.SUCCESS,
                    feasible=True,
                    objective_values=(initial_candidate.value,),
                    constraint_results=(),
                ),
            )

    hill_climbing = RecordingHillClimbing()
    experiment = MultiStartExperiment(hill_climbing=hill_climbing)
    problem = make_problem()

    result = experiment.optimize(
        problem,
        [
            CandidateDecision(2),
            CandidateDecision(8),
        ],
    )

    assert [candidate.value for candidate in hill_climbing.calls] == [2, 8]
    assert result.status is OptimizationStatus.SUCCESS
    assert result.best_candidate is not None
    assert result.best_candidate.value == 2
