
import pytest

from varopt import (
    CandidateDecision,
    EvaluationResult,
    EvaluationStatus,
    ObjectiveSense,
    OptimizationProblem,
    OptimizationStatus,
)
from varopt.experiments.beam_search_experiment import BeamSearchExperiment


class SimpleDecisionSpace:
    """Test-only decision space for bounded integer candidates."""

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


class ValueMaximizeObjective:
    """Test-only objective that maximizes the integer candidate value."""

    @property
    def name(self) -> str:
        return "value"

    @property
    def sense(self) -> ObjectiveSense:
        return ObjectiveSense.MAXIMIZE


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
    """Return the experiment's two-well objective."""
    return min((x - 2) ** 2, (x - 8) ** 2 + 2)


def neighbor_function(candidate: CandidateDecision) -> list[CandidateDecision]:
    """Return bounded adjacent candidates in x-1, then x+1 order."""
    x = candidate.value
    neighbors = []

    if x > 0:
        neighbors.append(CandidateDecision(x - 1))

    if x < 10:
        neighbors.append(CandidateDecision(x + 1))

    return neighbors


def make_problem(objective=None) -> OptimizationProblem:
    """Create a single-objective test problem."""
    if objective is None:
        objective = TwoWellMinimizeObjective()

    return OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(objective,),
        constraints=(),
    )


def make_experiment(
    *,
    beam_width: int = 2,
    max_steps: int = 10,
    evaluation=None,
    neighbors=neighbor_function,
) -> BeamSearchExperiment:
    """Create a concrete beam-search experiment."""
    if evaluation is None:
        evaluation = StubEvaluation(two_well_value)

    return BeamSearchExperiment(
        evaluation=evaluation,
        neighbor_function=neighbors,
        beam_width=beam_width,
        max_steps=max_steps,
    )


def assert_successful_result(result, expected_value, expected_objective):
    """Assert a result selects the expected candidate and objective."""
    assert result.status is OptimizationStatus.SUCCESS
    assert result.best_candidate is not None
    assert result.best_candidate.value == expected_value
    assert result.best_evaluation is not None
    assert result.best_evaluation.objective_values == (expected_objective,)


def test_wider_beam_preserves_an_alternative_path_to_better_solution():
    """A wider frontier reaches the global minimum from the same start."""
    problem = make_problem()

    narrow = make_experiment(beam_width=1).optimize(
        problem,
        [CandidateDecision(7)],
    )
    wide = make_experiment(beam_width=2).optimize(
        problem,
        [CandidateDecision(7)],
    )

    # Width one follows x=8 into the local-minimum basin.
    assert_successful_result(narrow, 8, 2)

    # Width two retains x=6 as an alternative and eventually reaches x=2.
    assert_successful_result(wide, 2, 0)


def test_beam_search_is_deterministic():
    """Identical ordered inputs and behavior produce identical results."""
    problem = make_problem()

    first = make_experiment(beam_width=2).optimize(
        problem,
        [CandidateDecision(7)],
    )
    second = make_experiment(beam_width=2).optimize(
        problem,
        [CandidateDecision(7)],
    )

    assert first.status is second.status
    assert first.best_candidate == second.best_candidate
    assert first.best_evaluation is not None
    assert second.best_evaluation is not None
    assert first.best_evaluation.objective_values == (
        second.best_evaluation.objective_values
    )


def test_beam_search_retains_first_result_on_equal_objectives():
    """Equal values preserve the first encountered candidate."""
    expanded = []

    def constant_neighbors(candidate: CandidateDecision):
        expanded.append(candidate.value)
        return []

    experiment = make_experiment(
        beam_width=1,
        evaluation=StubEvaluation(lambda _: 1),
        neighbors=constant_neighbors,
    )

    result = experiment.optimize(
        make_problem(),
        [CandidateDecision(4), CandidateDecision(6)],
    )

    assert_successful_result(result, 4, 1)
    assert expanded == [4]


def test_beam_search_deduplicates_candidates():
    """A candidate discovered more than once is evaluated only once."""
    evaluated = []

    class RecordingEvaluation:
        def evaluate(
            self,
            problem: OptimizationProblem,
            candidate: CandidateDecision,
        ) -> EvaluationResult:
            evaluated.append(candidate.value)
            return EvaluationResult(
                candidate=candidate,
                status=EvaluationStatus.SUCCESS,
                feasible=True,
                objective_values=(float(candidate.value),),
                constraint_results=(),
            )

    def duplicate_neighbors(candidate: CandidateDecision):
        if candidate.value == 5:
            return [
                CandidateDecision(4),
                CandidateDecision(4),
                CandidateDecision(6),
                CandidateDecision(6),
            ]
        return []

    experiment = make_experiment(
        beam_width=3,
        evaluation=RecordingEvaluation(),
        neighbors=duplicate_neighbors,
    )

    result = experiment.optimize(
        make_problem(),
        [CandidateDecision(5)],
    )

    assert evaluated == [5, 4, 6]
    assert_successful_result(result, 4, 4.0)


def test_beam_search_skips_failed_and_infeasible_candidates():
    """Failed and infeasible candidates cannot enter the active frontier."""

    class SelectiveEvaluation:
        def evaluate(
            self,
            problem: OptimizationProblem,
            candidate: CandidateDecision,
        ) -> EvaluationResult:
            if candidate.value == 4:
                return EvaluationResult(
                    candidate=candidate,
                    status=EvaluationStatus.FAILED,
                    feasible=None,
                    objective_values=(),
                    constraint_results=(),
                )

            if candidate.value == 6:
                return EvaluationResult(
                    candidate=candidate,
                    status=EvaluationStatus.SUCCESS,
                    feasible=False,
                    objective_values=(6,),
                    constraint_results=(),
                )

            return EvaluationResult(
                candidate=candidate,
                status=EvaluationStatus.SUCCESS,
                feasible=True,
                objective_values=(candidate.value,),
                constraint_results=(),
            )

    def selective_neighbors(candidate: CandidateDecision):
        if candidate.value == 5:
            return [
                CandidateDecision(4),
                CandidateDecision(6),
                CandidateDecision(3),
            ]
        return []

    experiment = make_experiment(
        beam_width=3,
        evaluation=SelectiveEvaluation(),
        neighbors=selective_neighbors,
    )

    result = experiment.optimize(
        make_problem(),
        [CandidateDecision(5)],
    )

    assert_successful_result(result, 3, 3)


def test_beam_search_returns_no_eligible_candidate_when_all_fail():
    """An entirely ineligible search returns the established empty result."""

    class FailedEvaluation:
        def evaluate(
            self,
            problem: OptimizationProblem,
            candidate: CandidateDecision,
        ) -> EvaluationResult:
            return EvaluationResult(
                candidate=candidate,
                status=EvaluationStatus.FAILED,
                feasible=None,
                objective_values=(),
                constraint_results=(),
            )

    experiment = make_experiment(evaluation=FailedEvaluation())

    result = experiment.optimize(
        make_problem(),
        [CandidateDecision(2), CandidateDecision(8)],
    )

    assert result.status is OptimizationStatus.NO_ELIGIBLE_CANDIDATE
    assert result.best_candidate is None
    assert result.best_evaluation is None


def test_beam_search_uses_maximize_objective_sense():
    """Frontier ranking and best-result selection support MAXIMIZE."""
    experiment = make_experiment(
        beam_width=1,
        max_steps=3,
        evaluation=StubEvaluation(float),
    )

    result = experiment.optimize(
        make_problem(ValueMaximizeObjective()),
        [CandidateDecision(5)],
    )

    assert_successful_result(result, 8, 8.0)


def test_beam_search_honors_step_limit():
    """The search expands the frontier no more than max_steps times."""
    expanded = []

    def increasing_neighbors(candidate: CandidateDecision):
        expanded.append(candidate.value)
        if candidate.value < 10:
            return [CandidateDecision(candidate.value + 1)]
        return []

    experiment = make_experiment(
        beam_width=1,
        max_steps=2,
        evaluation=StubEvaluation(float),
        neighbors=increasing_neighbors,
    )

    result = experiment.optimize(
        make_problem(ValueMaximizeObjective()),
        [CandidateDecision(0)],
    )

    assert_successful_result(result, 2, 2.0)
    assert expanded == [0, 1]


def test_beam_search_stops_when_no_neighbors_remain():
    """An empty neighborhood ends search and returns the best result."""
    experiment = make_experiment(neighbors=lambda _: [])

    result = experiment.optimize(
        make_problem(),
        [CandidateDecision(8)],
    )

    assert_successful_result(result, 8, 2)


@pytest.mark.parametrize(
    ("beam_width", "max_steps", "message"),
    [
        (0, 10, "Beam width must be positive."),
        (-1, 10, "Beam width must be positive."),
        (2, 0, "Maximum steps must be positive."),
        (2, -1, "Maximum steps must be positive."),
    ],
)
def test_beam_search_rejects_invalid_configuration(
    beam_width,
    max_steps,
    message,
):
    """Beam width and step limit must be positive."""
    with pytest.raises(ValueError, match=message):
        make_experiment(
            beam_width=beam_width,
            max_steps=max_steps,
        )


def test_beam_search_rejects_multiple_objectives():
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

    with pytest.raises(
        ValueError,
        match="The beam-search experiment requires exactly one objective.",
    ):
        experiment.optimize(problem, [CandidateDecision(2)])


def test_beam_search_handles_empty_initial_candidates():
    """An empty initial sequence yields no eligible result."""
    result = make_experiment().optimize(make_problem(), [])

    assert result.status is OptimizationStatus.NO_ELIGIBLE_CANDIDATE
    assert result.best_candidate is None
    assert result.best_evaluation is None