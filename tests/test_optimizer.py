from varopt import (
    CallableEvaluation,
    CandidateDecision,
    EvaluationResult,
    EvaluationStatus,
    ObjectiveSense,
    OptimizationProblem,
    OptimizationResult,
    OptimizationStatus,
    Optimizer,
)


class SimpleDecisionSpace:
    """Test-only decision space."""

    def is_representable(self, candidate: CandidateDecision) -> bool:
        return candidate.value is not None


class CompletionTimeObjective:
    """Manufacturing-shaped minimization objective."""

    @property
    def name(self) -> str:
        return "completion_time"

    @property
    def sense(self) -> ObjectiveSense:
        return ObjectiveSense.MINIMIZE


class FuelObjective:
    """Voyage-shaped minimization objective."""

    @property
    def name(self) -> str:
        return "fuel"

    @property
    def sense(self) -> ObjectiveSense:
        return ObjectiveSense.MINIMIZE


class ProductionRateObjective:
    """Manufacturing-shaped maximization objective."""

    @property
    def name(self) -> str:
        return "production_rate"

    @property
    def sense(self) -> ObjectiveSense:
        return ObjectiveSense.MAXIMIZE


class CapacityConstraint:
    """Test-only manufacturing constraint."""

    @property
    def name(self) -> str:
        return "capacity"

    def is_satisfied(self, candidate: CandidateDecision) -> bool:
        return candidate.value["load"] <= 100


class RouteConstraint:
    """Test-only voyage constraint."""

    @property
    def name(self) -> str:
        return "route"

    def is_satisfied(self, candidate: CandidateDecision) -> bool:
        return len(candidate.value["waypoints"]) >= 2


def test_optimizer_selects_lowest_minimization_objective():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(CompletionTimeObjective(),),
    )

    candidates = (
        CandidateDecision(value={"operations": 8}),
        CandidateDecision(value={"operations": 3}),
        CandidateDecision(value={"operations": 5}),
    )

    evaluation = CallableEvaluation(
        objective_functions=(
            lambda candidate: candidate.value["operations"] * 10,
        )
    )

    result = Optimizer(evaluation).optimize(problem, candidates)

    assert result.status == OptimizationStatus.SUCCESS
    assert result.best_candidate is candidates[1]
    assert result.best_evaluation is not None
    assert result.best_evaluation.objective_values == (30,)


def test_optimizer_selects_highest_maximization_objective():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(ProductionRateObjective(),),
    )

    candidates = (
        CandidateDecision(value={"rate": 40}),
        CandidateDecision(value={"rate": 75}),
        CandidateDecision(value={"rate": 55}),
    )

    evaluation = CallableEvaluation(
        objective_functions=(
            lambda candidate: candidate.value["rate"],
        )
    )

    result = Optimizer(evaluation).optimize(problem, candidates)

    assert result.status == OptimizationStatus.SUCCESS
    assert result.best_candidate is candidates[1]
    assert result.best_evaluation is not None
    assert result.best_evaluation.objective_values == (75,)


def test_equal_objective_values_retain_current_best():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(CompletionTimeObjective(),),
    )

    first = CandidateDecision(value={"operations": 5})
    second = CandidateDecision(value={"operations": 5})

    evaluation = CallableEvaluation(
        objective_functions=(
            lambda candidate: candidate.value["operations"],
        )
    )

    result = Optimizer(evaluation).optimize(
        problem,
        (first, second),
    )

    assert result.status == OptimizationStatus.SUCCESS
    assert result.best_candidate is first
    assert result.best_evaluation is not None
    assert result.best_evaluation.candidate is first


def test_successful_infeasible_candidates_are_not_eligible():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(CompletionTimeObjective(),),
        constraints=(CapacityConstraint(),),
    )

    candidates = (
        CandidateDecision(value={"operations": 1, "load": 150}),
        CandidateDecision(value={"operations": 5, "load": 75}),
    )

    evaluation = CallableEvaluation(
        objective_functions=(
            lambda candidate: candidate.value["operations"],
        )
    )

    result = Optimizer(evaluation).optimize(problem, candidates)

    assert result.status == OptimizationStatus.SUCCESS
    assert result.best_candidate is candidates[1]
    assert result.best_evaluation is not None
    assert result.best_evaluation.feasible is True


def test_failed_evaluations_are_skipped():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(CompletionTimeObjective(),),
    )

    candidates = (
        CandidateDecision(value="bad"),
        CandidateDecision(value={"operations": 7}),
        CandidateDecision(value={"operations": 4}),
    )

    def objective(candidate: CandidateDecision) -> int:
        if candidate.value == "bad":
            raise RuntimeError("evaluation failure")
        return candidate.value["operations"]

    evaluation = CallableEvaluation(
        objective_functions=(objective,),
    )

    result = Optimizer(evaluation).optimize(problem, candidates)

    assert result.status == OptimizationStatus.SUCCESS
    assert result.best_candidate is candidates[2]
    assert result.best_evaluation is not None
    assert result.best_evaluation.status is EvaluationStatus.SUCCESS


def test_no_constraints_feasible_none_is_eligible():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(CompletionTimeObjective(),),
    )

    candidates = (
        CandidateDecision(value={"operations": 8}),
        CandidateDecision(value={"operations": 3}),
    )

    evaluation = CallableEvaluation(
        objective_functions=(
            lambda candidate: candidate.value["operations"],
        )
    )

    result = Optimizer(evaluation).optimize(problem, candidates)

    assert result.status == OptimizationStatus.SUCCESS
    assert result.best_candidate is candidates[1]
    assert result.best_evaluation is not None
    assert result.best_evaluation.feasible is None


def test_empty_candidate_source_returns_no_eligible_candidate():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(CompletionTimeObjective(),),
    )

    evaluation = CallableEvaluation(
        objective_functions=(lambda candidate: 1,),
    )

    result = Optimizer(evaluation).optimize(problem, ())

    assert result.status == OptimizationStatus.NO_ELIGIBLE_CANDIDATE
    assert result.best_candidate is None
    assert result.best_evaluation is None


def test_all_infeasible_candidates_return_no_eligible_candidate():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(CompletionTimeObjective(),),
        constraints=(CapacityConstraint(),),
    )

    candidates = (
        CandidateDecision(value={"operations": 2, "load": 150}),
        CandidateDecision(value={"operations": 1, "load": 125}),
    )

    evaluation = CallableEvaluation(
        objective_functions=(
            lambda candidate: candidate.value["operations"],
        )
    )

    result = Optimizer(evaluation).optimize(problem, candidates)

    assert result.status == OptimizationStatus.NO_ELIGIBLE_CANDIDATE
    assert result.best_candidate is None
    assert result.best_evaluation is None


def test_all_failed_evaluations_return_no_eligible_candidate():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(CompletionTimeObjective(),),
    )

    candidates = (
        CandidateDecision(value="bad-1"),
        CandidateDecision(value="bad-2"),
    )

    def failing_objective(candidate: CandidateDecision) -> int:
        raise RuntimeError("evaluation failure")

    evaluation = CallableEvaluation(
        objective_functions=(failing_objective,),
    )

    result = Optimizer(evaluation).optimize(problem, candidates)

    assert result.status == OptimizationStatus.NO_ELIGIBLE_CANDIDATE
    assert result.best_candidate is None
    assert result.best_evaluation is None


def test_optimizer_accepts_generator_candidate_source():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(CompletionTimeObjective(),),
    )

    def candidates():
        yield CandidateDecision(value={"operations": 9})
        yield CandidateDecision(value={"operations": 2})
        yield CandidateDecision(value={"operations": 6})

    evaluation = CallableEvaluation(
        objective_functions=(
            lambda candidate: candidate.value["operations"],
        )
    )

    result = Optimizer(evaluation).optimize(problem, candidates())

    assert result.status == OptimizationStatus.SUCCESS
    assert result.best_candidate is not None
    assert result.best_candidate.value["operations"] == 2


def test_optimizer_exhausts_candidate_sequence():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(CompletionTimeObjective(),),
    )

    consumed = []

    def candidates():
        for value in (8, 5, 3):
            consumed.append(value)
            yield CandidateDecision(value={"operations": value})

    evaluation = CallableEvaluation(
        objective_functions=(
            lambda candidate: candidate.value["operations"],
        )
    )

    result = Optimizer(evaluation).optimize(problem, candidates())

    assert result.status == OptimizationStatus.SUCCESS
    assert consumed == [8, 5, 3]


def test_optimizer_requires_exactly_one_objective():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
    )

    evaluation = CallableEvaluation()

    try:
        Optimizer(evaluation).optimize(
            problem,
            (CandidateDecision(value="candidate"),),
        )
    except ValueError as exc:
        assert "exactly one objective" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_optimizer_rejects_multiple_objectives():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(
            CompletionTimeObjective(),
            FuelObjective(),
        ),
    )

    evaluation = CallableEvaluation(
        objective_functions=(
            lambda candidate: 1,
            lambda candidate: 2,
        )
    )

    try:
        Optimizer(evaluation).optimize(
            problem,
            (CandidateDecision(value="candidate"),),
        )
    except ValueError as exc:
        assert "exactly one objective" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_manufacturing_and_voyage_shapes_use_same_optimizer():
    forge_problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(CompletionTimeObjective(),),
        constraints=(CapacityConstraint(),),
    )

    nav_problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(FuelObjective(),),
        constraints=(RouteConstraint(),),
    )

    forge_candidates = (
        CandidateDecision(
            value={
                "operations": ("op-1", "op-2", "op-3"),
                "load": 80,
            }
        ),
        CandidateDecision(
            value={
                "operations": ("op-1", "op-2"),
                "load": 70,
            }
        ),
    )

    nav_candidates = (
        CandidateDecision(
            value={
                "waypoints": ("port-a", "port-b", "port-c"),
                "fuel": 250,
            }
        ),
        CandidateDecision(
            value={
                "waypoints": ("port-a", "port-b", "port-c", "port-d"),
                "fuel": 180,
            }
        ),
    )

    forge_evaluation = CallableEvaluation(
        objective_functions=(
            lambda candidate: len(candidate.value["operations"]) * 100,
        )
    )

    nav_evaluation = CallableEvaluation(
        objective_functions=(
            lambda candidate: candidate.value["fuel"],
        )
    )

    forge_result = Optimizer(forge_evaluation).optimize(
        forge_problem,
        forge_candidates,
    )

    nav_result = Optimizer(nav_evaluation).optimize(
        nav_problem,
        nav_candidates,
    )

    assert forge_result.status == OptimizationStatus.SUCCESS
    assert forge_result.best_candidate is forge_candidates[1]

    assert nav_result.status == OptimizationStatus.SUCCESS
    assert nav_result.best_candidate is nav_candidates[1]


def test_optimization_result_success_requires_selected_candidate_and_evaluation():
    try:
        OptimizationResult(status=OptimizationStatus.SUCCESS)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_optimization_result_no_candidate_requires_empty_selection():
    result = OptimizationResult(
        status=OptimizationStatus.NO_ELIGIBLE_CANDIDATE,
    )

    assert result.best_candidate is None
    assert result.best_evaluation is None
    
class StubEvaluation:
    """Test-only Evaluation implementation."""

    def __init__(self) -> None:
        self.evaluated_candidates = []

    def evaluate(
        self,
        problem: OptimizationProblem,
        candidate: CandidateDecision,
    ) -> EvaluationResult:
        self.evaluated_candidates.append(candidate)
        return EvaluationResult(
            candidate=candidate,
            status=EvaluationStatus.SUCCESS,
            feasible=None,
            objective_values=(candidate.value["operations"],),
        )


def test_optimizer_uses_evaluation_abstraction():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(CompletionTimeObjective(),),
    )

    candidates = (
        CandidateDecision(value={"operations": 8}),
        CandidateDecision(value={"operations": 3}),
        CandidateDecision(value={"operations": 5}),
    )

    evaluation = StubEvaluation()

    result = Optimizer(evaluation).optimize(problem, candidates)

    assert evaluation.evaluated_candidates == list(candidates)
    assert result.status == OptimizationStatus.SUCCESS
    assert result.best_candidate is candidates[1]
    assert result.best_evaluation is not None
    assert result.best_evaluation.candidate is candidates[1]
    assert result.best_evaluation.objective_values == (3,)