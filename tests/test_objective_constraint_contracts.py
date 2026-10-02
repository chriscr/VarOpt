from varopt import (
    CandidateDecision,
    Constraint,
    DecisionSpace,
    Objective,
    ObjectiveSense,
    OptimizationProblem,
)


class TestDecisionSpace:
    """Generic test-only decision space."""

    def is_representable(self, candidate: CandidateDecision) -> bool:
        return candidate.value is not None


class ManufacturingCompletionTimeObjective:
    """Test-only ForgeOpt-shaped objective."""

    @property
    def name(self) -> str:
        return "completion_time"

    @property
    def sense(self) -> ObjectiveSense:
        return ObjectiveSense.MINIMIZE


class ManufacturingCapacityConstraint:
    """Test-only ForgeOpt-shaped constraint."""

    @property
    def name(self) -> str:
        return "machine_capacity"

    def is_satisfied(self, candidate: CandidateDecision) -> bool:
        return isinstance(candidate.value, dict)


class VoyageFuelObjective:
    """Test-only NavOpt-shaped objective."""

    @property
    def name(self) -> str:
        return "fuel_consumption"

    @property
    def sense(self) -> ObjectiveSense:
        return ObjectiveSense.MINIMIZE


class VoyageFuelCapacityConstraint:
    """Test-only NavOpt-shaped constraint."""

    @property
    def name(self) -> str:
        return "fuel_capacity"

    def is_satisfied(self, candidate: CandidateDecision) -> bool:
        return isinstance(candidate.value, tuple)


class NetworkReliabilityObjective:
    """Test-only NexaOpt-shaped objective."""

    @property
    def name(self) -> str:
        return "network_reliability"

    @property
    def sense(self) -> ObjectiveSense:
        return ObjectiveSense.MAXIMIZE


class NetworkCapacityConstraint:
    """Test-only NexaOpt-shaped constraint."""

    @property
    def name(self) -> str:
        return "network_capacity"

    def is_satisfied(self, candidate: CandidateDecision) -> bool:
        return isinstance(candidate.value, frozenset)


def test_objective_expresses_optimization_direction():
    objective: Objective = ManufacturingCompletionTimeObjective()

    assert objective.name == "completion_time"
    assert objective.sense is ObjectiveSense.MINIMIZE


def test_constraint_expresses_admissibility():
    constraint: Constraint = ManufacturingCapacityConstraint()
    candidate = CandidateDecision(
        value={"operations": ("op-1", "op-2")}
    )

    assert constraint.name == "machine_capacity"
    assert constraint.is_satisfied(candidate)


def test_objectives_support_both_directions():
    minimizing: Objective = VoyageFuelObjective()
    maximizing: Objective = NetworkReliabilityObjective()

    assert minimizing.sense is ObjectiveSense.MINIMIZE
    assert maximizing.sense is ObjectiveSense.MAXIMIZE


def test_problem_can_contain_objectives_and_constraints():
    decision_space: DecisionSpace = TestDecisionSpace()
    problem = OptimizationProblem(
        decision_space=decision_space,
        objectives=(ManufacturingCompletionTimeObjective(),),
        constraints=(ManufacturingCapacityConstraint(),),
    )

    assert problem.decision_space is decision_space
    assert len(problem.objectives) == 1
    assert len(problem.constraints) == 1
    assert problem.objectives[0].name == "completion_time"
    assert problem.constraints[0].name == "machine_capacity"


def test_objectives_and_constraints_remain_distinct():
    objective = VoyageFuelObjective()
    constraint = VoyageFuelCapacityConstraint()
    candidate = CandidateDecision(
        value=("port-a", "port-b")
    )

    assert objective.sense is ObjectiveSense.MINIMIZE
    assert constraint.is_satisfied(candidate)


def test_domain_specific_objective_and_constraint_shapes():
    objective: Objective = NetworkReliabilityObjective()
    constraint: Constraint = NetworkCapacityConstraint()

    candidate = CandidateDecision(
        value=frozenset(
            {
                ("node-a", "node-b"),
                ("node-b", "node-c"),
            }
        )
    )

    assert objective.sense is ObjectiveSense.MAXIMIZE
    assert constraint.is_satisfied(candidate)


def test_problem_allows_multiple_objectives():
    decision_space: DecisionSpace = TestDecisionSpace()
    problem = OptimizationProblem(
        decision_space=decision_space,
        objectives=(
            ManufacturingCompletionTimeObjective(),
            VoyageFuelObjective(),
        ),
    )

    assert len(problem.objectives) == 2
    assert problem.constraints == ()


def test_problem_allows_no_objectives_and_no_constraints():
    decision_space: DecisionSpace = TestDecisionSpace()
    problem = OptimizationProblem(
        decision_space=decision_space,
    )

    assert problem.objectives == ()
    assert problem.constraints == ()