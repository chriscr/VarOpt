from dataclasses import FrozenInstanceError, fields

import pytest

from varopt import (
    CandidateDecision,
    Constraint,
    DecisionSpace,
    Objective,
    ObjectiveSense,
    OptimizationProblem,
)


class MinimalDecisionSpace:
    """Test-only decision space with no feasibility responsibility."""

    def is_representable(self, candidate: CandidateDecision) -> bool:
        return candidate.value is not None


class RejectingConstraint:
    """Test-only constraint that rejects every candidate."""

    @property
    def name(self) -> str:
        return "always_reject"

    def is_satisfied(self, candidate: CandidateDecision) -> bool:
        return False


class MinimizingObjective:
    """Test-only objective."""

    @property
    def name(self) -> str:
        return "test_objective"

    @property
    def sense(self) -> ObjectiveSense:
        return ObjectiveSense.MINIMIZE


def test_candidate_value_is_preserved_unchanged():
    decision = {"route": ("A", "B", "C")}
    candidate = CandidateDecision(value=decision)

    assert candidate.value is decision


def test_candidate_is_top_level_immutable():
    candidate = CandidateDecision(value=42)

    with pytest.raises(FrozenInstanceError):
        candidate.value = 99


def test_optimization_problem_is_top_level_immutable():
    decision_space: DecisionSpace = MinimalDecisionSpace()
    problem = OptimizationProblem(decision_space=decision_space)

    with pytest.raises(FrozenInstanceError):
        problem.decision_space = MinimalDecisionSpace()


def test_problem_has_explicit_zero_or_more_collections():
    problem = OptimizationProblem(
        decision_space=MinimalDecisionSpace(),
    )

    assert problem.objectives == ()
    assert problem.constraints == ()
    assert isinstance(problem.objectives, tuple)
    assert isinstance(problem.constraints, tuple)


def test_problem_preserves_objective_and_constraint_order():
    objective = MinimizingObjective()
    constraint = RejectingConstraint()

    problem = OptimizationProblem(
        decision_space=MinimalDecisionSpace(),
        objectives=(objective,),
        constraints=(constraint,),
    )

    assert problem.objectives == (objective,)
    assert problem.constraints == (constraint,)


def test_candidate_can_be_representable_but_infeasible():
    candidate = CandidateDecision(value="valid-shape")

    decision_space: DecisionSpace = MinimalDecisionSpace()
    constraint: Constraint = RejectingConstraint()

    assert decision_space.is_representable(candidate)
    assert not constraint.is_satisfied(candidate)


def test_objective_and_constraint_are_separate_contracts():
    objective: Objective = MinimizingObjective()
    constraint: Constraint = RejectingConstraint()

    assert objective.name == "test_objective"
    assert objective.sense is ObjectiveSense.MINIMIZE
    assert constraint.name == "always_reject"


def test_problem_contains_only_core_definition_fields():
    problem = OptimizationProblem(
        decision_space=MinimalDecisionSpace(),
        objectives=(MinimizingObjective(),),
        constraints=(RejectingConstraint(),),
    )

    field_names = {field.name for field in fields(problem)}

    assert field_names == {
        "decision_space",
        "objectives",
        "constraints",
    }