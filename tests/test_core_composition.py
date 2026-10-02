from varopt import (
    CandidateDecision,
    Constraint,
    DecisionSpace,
    Objective,
    ObjectiveSense,
    OptimizationProblem,
)


class ProductionScheduleSpace:
    """Test-only domain-shaped decision space."""

    def is_representable(self, candidate: CandidateDecision) -> bool:
        value = candidate.value

        return (
            isinstance(value, dict)
            and isinstance(value.get("operations"), tuple)
            and all(isinstance(operation, str) for operation in value["operations"])
        )


class CompletionTimeObjective:
    """Test-only objective for the composed problem."""

    @property
    def name(self) -> str:
        return "completion_time"

    @property
    def sense(self) -> ObjectiveSense:
        return ObjectiveSense.MINIMIZE


class ProductionCapacityConstraint:
    """Test-only constraint for the composed problem."""

    @property
    def name(self) -> str:
        return "production_capacity"

    def is_satisfied(self, candidate: CandidateDecision) -> bool:
        value = candidate.value

        if not isinstance(value, dict):
            return False

        operations = value.get("operations")

        return isinstance(operations, tuple) and len(operations) <= 3


def test_core_abstractions_compose_into_a_problem():
    decision_space: DecisionSpace = ProductionScheduleSpace()
    objective: Objective = CompletionTimeObjective()
    constraint: Constraint = ProductionCapacityConstraint()

    problem = OptimizationProblem(
        decision_space=decision_space,
        objectives=(objective,),
        constraints=(constraint,),
    )

    candidate = CandidateDecision(
        value={
            "operations": ("op-1", "op-2"),
        }
    )

    assert problem.decision_space.is_representable(candidate)
    assert problem.constraints[0].is_satisfied(candidate)
    assert problem.objectives[0].sense is ObjectiveSense.MINIMIZE


def test_composed_problem_preserves_each_boundary():
    decision_space: DecisionSpace = ProductionScheduleSpace()
    objective: Objective = CompletionTimeObjective()
    constraint: Constraint = ProductionCapacityConstraint()

    problem = OptimizationProblem(
        decision_space=decision_space,
        objectives=(objective,),
        constraints=(constraint,),
    )

    assert problem.decision_space is decision_space
    assert problem.objectives == (objective,)
    assert problem.constraints == (constraint,)


def test_composed_problem_rejects_structurally_invalid_candidate():
    decision_space: DecisionSpace = ProductionScheduleSpace()
    constraint: Constraint = ProductionCapacityConstraint()

    problem = OptimizationProblem(
        decision_space=decision_space,
        constraints=(constraint,),
    )

    candidate = CandidateDecision(
        value={
            "not_operations": ("op-1", "op-2"),
        }
    )

    assert not problem.decision_space.is_representable(candidate)


def test_composed_problem_can_have_representable_but_infeasible_candidate():
    decision_space: DecisionSpace = ProductionScheduleSpace()
    constraint: Constraint = ProductionCapacityConstraint()

    problem = OptimizationProblem(
        decision_space=decision_space,
        constraints=(constraint,),
    )

    candidate = CandidateDecision(
        value={
            "operations": ("op-1", "op-2", "op-3", "op-4"),
        }
    )

    assert problem.decision_space.is_representable(candidate)
    assert not problem.constraints[0].is_satisfied(candidate)


def test_composed_problem_can_contain_multiple_objectives_and_constraints():
    decision_space: DecisionSpace = ProductionScheduleSpace()
    objective_1: Objective = CompletionTimeObjective()
    objective_2: Objective = CompletionTimeObjective()
    constraint_1: Constraint = ProductionCapacityConstraint()
    constraint_2: Constraint = ProductionCapacityConstraint()

    problem = OptimizationProblem(
        decision_space=decision_space,
        objectives=(objective_1, objective_2),
        constraints=(constraint_1, constraint_2),
    )

    assert len(problem.objectives) == 2
    assert len(problem.constraints) == 2