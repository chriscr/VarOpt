import pytest

from varopt import (
    CandidateDecision,
    Evaluation,
    EvaluationResult,
    EvaluationStatus,
    ObjectiveSense,
    OptimizationProblem,
)


class SimpleDecisionSpace:
    """Test-only domain-neutral decision space."""

    def is_representable(self, candidate: CandidateDecision) -> bool:
        return candidate.value is not None


class ManufacturingEvaluation:
    """Test-only ForgeOpt-shaped evaluation."""

    def evaluate(
        self,
        problem: OptimizationProblem,
        candidate: CandidateDecision,
    ) -> EvaluationResult:
        return EvaluationResult(
            candidate=candidate,
            status=EvaluationStatus.SUCCESS,
            feasible=True,
            objective_values=(100.0,),
            constraint_results=(True,),
        )


class VoyageEvaluation:
    """Test-only NavOpt-shaped evaluation."""

    def evaluate(
        self,
        problem: OptimizationProblem,
        candidate: CandidateDecision,
    ) -> EvaluationResult:
        return EvaluationResult(
            candidate=candidate,
            status=EvaluationStatus.SUCCESS,
            feasible=False,
            objective_values=(250.0,),
            constraint_results=(False,),
        )


class NetworkEvaluation:
    """Test-only NexaOpt-shaped evaluation."""

    def evaluate(
        self,
        problem: OptimizationProblem,
        candidate: CandidateDecision,
    ) -> EvaluationResult:
        return EvaluationResult(
            candidate=candidate,
            status=EvaluationStatus.SUCCESS,
            feasible=True,
            objective_values=(0.97,),
            constraint_results=(True, True),
        )


class FailedEvaluation:
    """Test-only evaluation that cannot establish a result."""

    def evaluate(
        self,
        problem: OptimizationProblem,
        candidate: CandidateDecision,
    ) -> EvaluationResult:
        return EvaluationResult(
            candidate=candidate,
            status=EvaluationStatus.FAILED,
            feasible=None,
        )


def make_problem() -> OptimizationProblem:
    """Create a minimal problem for boundary tests."""

    return OptimizationProblem(
        decision_space=SimpleDecisionSpace(),
    )


def test_evaluation_protocol_accepts_concrete_implementation():
    evaluation: Evaluation = ManufacturingEvaluation()

    candidate = CandidateDecision(
        value={"operations": ("op-1", "op-2")}
    )

    result = evaluation.evaluate(make_problem(), candidate)

    assert isinstance(result, EvaluationResult)
    assert result.candidate is candidate
    assert result.status is EvaluationStatus.SUCCESS


def test_successful_feasible_evaluation_is_distinct_from_failure():
    evaluation: Evaluation = ManufacturingEvaluation()

    result = evaluation.evaluate(
        make_problem(),
        CandidateDecision(value="manufacturing-plan"),
    )

    assert result.status is EvaluationStatus.SUCCESS
    assert result.feasible is True


def test_successful_infeasible_evaluation_is_not_evaluation_failure():
    evaluation: Evaluation = VoyageEvaluation()

    result = evaluation.evaluate(
        make_problem(),
        CandidateDecision(value=("port-a", "port-b")),
    )

    assert result.status is EvaluationStatus.SUCCESS
    assert result.feasible is False
    assert result.constraint_results == (False,)


def test_failed_evaluation_does_not_imply_infeasibility():
    evaluation: Evaluation = FailedEvaluation()

    result = evaluation.evaluate(
        make_problem(),
        CandidateDecision(value="unavailable-evaluation"),
    )

    assert result.status is EvaluationStatus.FAILED
    assert result.feasible is None
    assert result.objective_values == ()
    assert result.constraint_results == ()

def test_failed_evaluation_preserves_unknown_feasibility():
    result = EvaluationResult(
        candidate=CandidateDecision({"example": "decision"}),
        status=EvaluationStatus.FAILED,
        feasible=None,
    )

    assert result.status is EvaluationStatus.FAILED
    assert result.feasible is None

@pytest.mark.parametrize("feasible", [True, False])
def test_failed_evaluation_cannot_establish_feasibility(feasible):
    with pytest.raises(
        ValueError,
        match="A failed evaluation must not establish feasibility",
    ):
        EvaluationResult(
            candidate=CandidateDecision({"example": "decision"}),
            status=EvaluationStatus.FAILED,
            feasible=feasible,
        )

def test_evaluation_result_preserves_candidate_identity():
    candidate = CandidateDecision(value="candidate")

    result = ManufacturingEvaluation().evaluate(
        make_problem(),
        candidate,
    )

    assert result.candidate is candidate


def test_objective_values_are_preserved_in_order():
    result = NetworkEvaluation().evaluate(
        make_problem(),
        CandidateDecision(value="network"),
    )

    assert result.objective_values == (0.97,)


def test_constraint_results_are_preserved_in_order():
    result = NetworkEvaluation().evaluate(
        make_problem(),
        CandidateDecision(value="network"),
    )

    assert result.constraint_results == (True, True)


def test_different_domain_evaluations_share_the_same_boundary():
    evaluations: list[Evaluation] = [
        ManufacturingEvaluation(),
        VoyageEvaluation(),
        NetworkEvaluation(),
    ]

    candidates = [
        CandidateDecision(value={"operations": ("op-1", "op-2")}),
        CandidateDecision(value=("port-a", "port-b")),
        CandidateDecision(value=frozenset({("node-a", "node-b")})),
    ]

    results = [
        evaluation.evaluate(make_problem(), candidate)
        for evaluation, candidate in zip(evaluations, candidates)
    ]

    assert all(isinstance(result, EvaluationResult) for result in results)
    assert all(
        result.status is EvaluationStatus.SUCCESS
        for result in results
    )


def test_failed_evaluation_remains_a_result():
    candidate = CandidateDecision(value="candidate")

    result = FailedEvaluation().evaluate(
        make_problem(),
        candidate,
    )

    assert result.candidate is candidate
    assert result.status is EvaluationStatus.FAILED


def test_evaluation_result_is_immutable():
    result = ManufacturingEvaluation().evaluate(
        make_problem(),
        CandidateDecision(value="candidate"),
    )

    try:
        result.feasible = False
    except AttributeError:
        pass
    else:
        raise AssertionError("EvaluationResult should be immutable")


def test_evaluation_does_not_define_optimization_direction():
    result = ManufacturingEvaluation().evaluate(
        make_problem(),
        CandidateDecision(value="candidate"),
    )

    assert result.status is EvaluationStatus.SUCCESS
    assert result.feasible is True

    # Objective direction belongs to the Objective contract, not EvaluationResult.
    assert ObjectiveSense.MINIMIZE.value == "minimize"
