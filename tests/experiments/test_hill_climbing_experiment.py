from varopt import (
    CandidateDecision,
    EvaluationResult,
    EvaluationStatus,
    ObjectiveSense,
    OptimizationProblem,
    OptimizationStatus,
)
from varopt.experiments.hill_climbing_experiment import HillClimbingExperiment


class SimpleDecisionSpace:
    """Test-only decision space for integer candidates."""

    def is_representable(self, candidate: CandidateDecision) -> bool:
        return isinstance(candidate.value, int) and 0 <= candidate.value <= 10


class QuadraticMinimizeObjective:
    """Test-only minimization objective."""

    @property
    def name(self) -> str:
        return "quadratic"

    @property
    def sense(self) -> ObjectiveSense:
        return ObjectiveSense.MINIMIZE


class QuadraticMaximizeObjective:
    """Test-only maximization objective."""

    @property
    def name(self) -> str:
        return "quadratic"

    @property
    def sense(self) -> ObjectiveSense:
        return ObjectiveSense.MAXIMIZE


class StubEvaluation:
    """Test-only deterministic evaluation implementation."""

    def __init__(self, objective_function, feasible_function=None) -> None:
        self.objective_function = objective_function
        self.feasible_function = feasible_function
        self.evaluated_candidates = []

    def evaluate(
        self,
        problem: OptimizationProblem,
        candidate: CandidateDecision,
    ) -> EvaluationResult:
        self.evaluated_candidates.append(candidate)

        try:
            objective_value = self.objective_function(candidate)
        except RuntimeError:
            return EvaluationResult(
                candidate=candidate,
                status=EvaluationStatus.FAILED,
                feasible=None,
            )

        feasible = None
        if self.feasible_function is not None:
            feasible = self.feasible_function(candidate)

        return EvaluationResult(
            candidate=candidate,
            status=EvaluationStatus.SUCCESS,
            feasible=feasible,
            objective_values=(objective_value,),
        )


def test_hill_climbing_reaches_minimum_from_initial_candidate():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(QuadraticMinimizeObjective(),),
    )

    evaluation = StubEvaluation(
        objective_function=lambda candidate: (candidate.value - 7) ** 2,
    )

    def neighbors(candidate: CandidateDecision) -> list[CandidateDecision]:
        value = candidate.value
        result = []

        if value > 0:
            result.append(CandidateDecision(value=value - 1))

        if value < 10:
            result.append(CandidateDecision(value=value + 1))

        return result

    initial_candidate = CandidateDecision(value=2)

    result = HillClimbingExperiment(
        evaluation=evaluation,
        neighbor_function=neighbors,
    ).optimize(
        problem,
        initial_candidate,
    )

    assert result.status is OptimizationStatus.SUCCESS
    assert result.best_candidate is not None
    assert result.best_candidate.value == 7
    assert result.best_evaluation is not None
    assert result.best_evaluation.objective_values == (0,)


def test_hill_climbing_stops_when_no_neighbor_is_strictly_better():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(QuadraticMinimizeObjective(),),
    )

    evaluation = StubEvaluation(
        objective_function=lambda candidate: (candidate.value - 7) ** 2,
    )

    neighbor_values = []

    def neighbors(candidate: CandidateDecision) -> list[CandidateDecision]:
        value = candidate.value
        result = []

        if value > 0:
            result.append(CandidateDecision(value=value - 1))

        if value < 10:
            result.append(CandidateDecision(value=value + 1))

        neighbor_values.append(value)
        return result

    initial_candidate = CandidateDecision(value=7)

    result = HillClimbingExperiment(
        evaluation=evaluation,
        neighbor_function=neighbors,
    ).optimize(
        problem,
        initial_candidate,
    )

    assert result.status is OptimizationStatus.SUCCESS
    assert result.best_candidate is initial_candidate
    assert result.best_evaluation is not None
    assert result.best_evaluation.objective_values == (0,)
    assert neighbor_values == [7]


def test_hill_climbing_uses_objective_sense_for_maximization():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(QuadraticMaximizeObjective(),),
    )

    evaluation = StubEvaluation(
        objective_function=lambda candidate: -(candidate.value - 7) ** 2,
    )

    def neighbors(candidate: CandidateDecision) -> list[CandidateDecision]:
        value = candidate.value
        result = []

        if value > 0:
            result.append(CandidateDecision(value=value - 1))

        if value < 10:
            result.append(CandidateDecision(value=value + 1))

        return result

    initial_candidate = CandidateDecision(value=2)

    result = HillClimbingExperiment(
        evaluation=evaluation,
        neighbor_function=neighbors,
    ).optimize(
        problem,
        initial_candidate,
    )

    assert result.status is OptimizationStatus.SUCCESS
    assert result.best_candidate is not None
    assert result.best_candidate.value == 7
    assert result.best_evaluation is not None
    assert result.best_evaluation.objective_values == (0,)


def test_hill_climbing_ignores_infeasible_neighbors():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(QuadraticMinimizeObjective(),),
        constraints=("test constraint",),
    )

    evaluation = StubEvaluation(
        objective_function=lambda candidate: (candidate.value - 7) ** 2,
        feasible_function=lambda candidate: candidate.value <= 5,
    )

    def neighbors(candidate: CandidateDecision) -> list[CandidateDecision]:
        value = candidate.value
        result = []

        if value > 0:
            result.append(CandidateDecision(value=value - 1))

        if value < 10:
            result.append(CandidateDecision(value=value + 1))

        return result

    initial_candidate = CandidateDecision(value=5)

    result = HillClimbingExperiment(
        evaluation=evaluation,
        neighbor_function=neighbors,
    ).optimize(
        problem,
        initial_candidate,
    )

    assert result.status is OptimizationStatus.SUCCESS
    assert result.best_candidate is initial_candidate
    assert result.best_evaluation is not None
    assert result.best_evaluation.feasible is True
    assert result.best_evaluation.objective_values == (4,)


def test_hill_climbing_skips_failed_neighbor_evaluations():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(QuadraticMinimizeObjective(),),
    )

    def objective(candidate: CandidateDecision) -> int:
        if candidate.value == 4:
            raise RuntimeError("evaluation failure")

        return (candidate.value - 7) ** 2

    evaluation = StubEvaluation(
        objective_function=objective,
    )

    def neighbors(candidate: CandidateDecision) -> list[CandidateDecision]:
        value = candidate.value

        if value == 2:
            return [
                CandidateDecision(value=3),
                CandidateDecision(value=4),
            ]

        result = []

        if value > 0:
            result.append(CandidateDecision(value=value - 1))

        if value < 10:
            result.append(CandidateDecision(value=value + 1))

        return result

    initial_candidate = CandidateDecision(value=2)

    result = HillClimbingExperiment(
        evaluation=evaluation,
        neighbor_function=neighbors,
    ).optimize(
        problem,
        initial_candidate,
    )

    assert result.status is OptimizationStatus.SUCCESS
    assert result.best_candidate is not None
    assert result.best_candidate.value == 3
    assert result.best_evaluation is not None
    assert result.best_evaluation.objective_values == (16,)
    assert 4 in [
        candidate.value for candidate in evaluation.evaluated_candidates
    ]


def test_hill_climbing_returns_no_eligible_candidate_for_ineligible_start():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(QuadraticMinimizeObjective(),),
        constraints=("test constraint",),
    )

    evaluation = StubEvaluation(
        objective_function=lambda candidate: (candidate.value - 7) ** 2,
        feasible_function=lambda candidate: False,
    )

    def neighbors(candidate: CandidateDecision) -> list[CandidateDecision]:
        return [
            CandidateDecision(value=candidate.value - 1),
            CandidateDecision(value=candidate.value + 1),
        ]

    result = HillClimbingExperiment(
        evaluation=evaluation,
        neighbor_function=neighbors,
    ).optimize(
        problem,
        CandidateDecision(value=2),
    )

    assert result.status is OptimizationStatus.NO_ELIGIBLE_CANDIDATE
    assert result.best_candidate is None
    assert result.best_evaluation is None


def test_hill_climbing_uses_evaluation_abstraction():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(QuadraticMinimizeObjective(),),
    )

    evaluation = StubEvaluation(
        objective_function=lambda candidate: (candidate.value - 7) ** 2,
    )

    def neighbors(candidate: CandidateDecision) -> list[CandidateDecision]:
        value = candidate.value

        if value < 7:
            return [CandidateDecision(value=value + 1)]

        if value > 7:
            return [CandidateDecision(value=value - 1)]

        return []

    initial_candidate = CandidateDecision(value=5)

    result = HillClimbingExperiment(
        evaluation=evaluation,
        neighbor_function=neighbors,
    ).optimize(
        problem,
        initial_candidate,
    )

    assert result.status is OptimizationStatus.SUCCESS
    assert result.best_candidate is not None
    assert result.best_candidate.value == 7
    assert evaluation.evaluated_candidates
    assert all(
        isinstance(candidate, CandidateDecision)
        for candidate in evaluation.evaluated_candidates
    )


def test_hill_climbing_rejects_multiple_objectives():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(
            QuadraticMinimizeObjective(),
            QuadraticMinimizeObjective(),
        ),
    )

    evaluation = StubEvaluation(
        objective_function=lambda candidate: (candidate.value - 7) ** 2,
    )

    try:
        HillClimbingExperiment(
            evaluation=evaluation,
            neighbor_function=lambda candidate: [],
        ).optimize(
            problem,
            CandidateDecision(value=2),
        )
    except ValueError as exc:
        assert "exactly one objective" in str(exc)
    else:
        raise AssertionError("Expected ValueError")