from varopt import (
    CallableEvaluation,
    CandidateDecision,
    Evaluation,
    EvaluationStatus,
    ObjectiveSense,
    OptimizationProblem,
)


class SimpleDecisionSpace:
    """Test-only decision space."""

    def is_representable(self, candidate: CandidateDecision) -> bool:
        return candidate.value is not None


class CompletionTimeObjective:
    """Test-only manufacturing objective."""

    @property
    def name(self) -> str:
        return "completion_time"

    @property
    def sense(self) -> ObjectiveSense:
        return ObjectiveSense.MINIMIZE


class FuelObjective:
    """Test-only voyage objective."""

    @property
    def name(self) -> str:
        return "fuel"

    @property
    def sense(self) -> ObjectiveSense:
        return ObjectiveSense.MINIMIZE


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


def test_callable_evaluation_implements_evaluation_boundary():
    evaluation: Evaluation = CallableEvaluation()

    assert isinstance(evaluation, CallableEvaluation)


def test_callable_evaluation_computes_objective_value():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(CompletionTimeObjective(),),
    )

    candidate = CandidateDecision(
        value={"operations": 5},
    )

    evaluation = CallableEvaluation(
        objective_functions=(
            lambda candidate: candidate.value["operations"] * 10,
        )
    )

    result = evaluation.evaluate(problem, candidate)

    assert result.status is EvaluationStatus.SUCCESS
    assert result.objective_values == (50,)
    assert result.candidate is candidate


def test_multiple_objectives_preserve_positional_order():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(
            CompletionTimeObjective(),
            FuelObjective(),
        ),
    )

    candidate = CandidateDecision(
        value={"time": 12, "fuel": 37},
    )

    evaluation = CallableEvaluation(
        objective_functions=(
            lambda candidate: candidate.value["time"],
            lambda candidate: candidate.value["fuel"],
        )
    )

    result = evaluation.evaluate(problem, candidate)

    assert result.status is EvaluationStatus.SUCCESS
    assert result.objective_values == (12, 37)


def test_satisfied_constraints_establish_feasibility():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        constraints=(CapacityConstraint(),),
    )

    candidate = CandidateDecision(
        value={"load": 75},
    )

    result = CallableEvaluation().evaluate(problem, candidate)

    assert result.status is EvaluationStatus.SUCCESS
    assert result.constraint_results == (True,)
    assert result.feasible is True


def test_failed_constraint_establishes_infeasibility_not_evaluation_failure():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        constraints=(CapacityConstraint(),),
    )

    candidate = CandidateDecision(
        value={"load": 125},
    )

    result = CallableEvaluation().evaluate(problem, candidate)

    assert result.status is EvaluationStatus.SUCCESS
    assert result.constraint_results == (False,)
    assert result.feasible is False


def test_multiple_constraints_preserve_positional_order():
    class SecondConstraint:
        @property
        def name(self) -> str:
            return "second"

        def is_satisfied(self, candidate: CandidateDecision) -> bool:
            return True

    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        constraints=(CapacityConstraint(), SecondConstraint()),
    )

    candidate = CandidateDecision(
        value={"load": 75},
    )

    result = CallableEvaluation().evaluate(problem, candidate)

    assert result.status is EvaluationStatus.SUCCESS
    assert result.constraint_results == (True, True)
    assert result.feasible is True


def test_no_constraints_do_not_automatically_establish_feasibility():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
    )

    candidate = CandidateDecision(value="candidate")

    result = CallableEvaluation().evaluate(problem, candidate)

    assert result.status is EvaluationStatus.SUCCESS
    assert result.constraint_results == ()
    assert result.feasible is None


def test_objective_evaluation_failure_is_distinct_from_infeasibility():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(CompletionTimeObjective(),),
    )

    candidate = CandidateDecision(value="invalid-for-objective")

    def failing_objective(candidate: CandidateDecision) -> float:
        raise RuntimeError("evaluation unavailable")

    result = CallableEvaluation(
        objective_functions=(failing_objective,),
    ).evaluate(problem, candidate)

    assert result.status is EvaluationStatus.FAILED
    assert result.feasible is None
    assert result.objective_values == ()
    assert result.constraint_results == ()
    assert result.candidate is candidate


def test_objective_function_count_mismatch_is_evaluation_failure():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(
            CompletionTimeObjective(),
            FuelObjective(),
        ),
    )

    candidate = CandidateDecision(value={"time": 10, "fuel": 20})

    evaluation = CallableEvaluation(
        objective_functions=(
            lambda candidate: candidate.value["time"],
        )
    )

    result = evaluation.evaluate(problem, candidate)

    assert result.status is EvaluationStatus.FAILED
    assert result.feasible is None


def test_forgeopt_and_navopt_shaped_candidates_use_same_evaluation_mechanism():
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

    forge_candidate = CandidateDecision(
        value={
            "operations": ("op-1", "op-2"),
            "load": 80,
        }
    )

    nav_candidate = CandidateDecision(
        value={
            "waypoints": ("port-a", "port-b", "port-c"),
            "fuel": 250,
        }
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

    forge_result = forge_evaluation.evaluate(
        forge_problem,
        forge_candidate,
    )

    nav_result = nav_evaluation.evaluate(
        nav_problem,
        nav_candidate,
    )

    assert forge_result.status is EvaluationStatus.SUCCESS
    assert forge_result.feasible is True
    assert forge_result.objective_values == (200,)
    assert forge_result.constraint_results == (True,)

    assert nav_result.status is EvaluationStatus.SUCCESS
    assert nav_result.feasible is True
    assert nav_result.objective_values == (250,)
    assert nav_result.constraint_results == (True,)


def test_deterministic_evaluation_repeats_same_result():
    problem = OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
        objectives=(CompletionTimeObjective(),),
        constraints=(CapacityConstraint(),),
    )

    candidate = CandidateDecision(
        value={"operations": 4, "load": 60},
    )

    evaluation = CallableEvaluation(
        objective_functions=(
            lambda candidate: candidate.value["operations"] * 25,
        )
    )

    first = evaluation.evaluate(problem, candidate)
    second = evaluation.evaluate(problem, candidate)

    assert first == second