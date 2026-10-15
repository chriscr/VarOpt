import math

import pytest

from varopt import (
    CandidateDecision,
    EvaluationStatus,
    ObjectiveSense,
    OptimizationProblem,
)
from varopt.experiments.inventory_evaluation_experiment import (
    InventoryContext,
    InventoryDecisionSpace,
    InventoryEvaluationExperiment,
)


class MinimizeCostObjective:
    @property
    def name(self) -> str:
        return "total_inventory_cost"

    @property
    def sense(self) -> ObjectiveSense:
        return ObjectiveSense.MINIMIZE


class MaximizeCostObjective:
    @property
    def name(self) -> str:
        return "total_inventory_cost"

    @property
    def sense(self) -> ObjectiveSense:
        return ObjectiveSense.MAXIMIZE


def make_context(**overrides) -> InventoryContext:
    values = {
        "initial_inventory": 1,
        "demand": (2, 1),
        "production_cost": 2,
        "holding_cost": 1,
        "shortage_penalty": 5,
    }
    values.update(overrides)
    return InventoryContext(**values)


def make_problem(context: InventoryContext, objective=None) -> OptimizationProblem:
    return OptimizationProblem(
        decision_space=InventoryDecisionSpace(len(context.demand)),
        objectives=(objective or MinimizeCostObjective(),),
    )


def evaluate(plan, context=None, problem=None):
    context = context or make_context()
    problem = problem or make_problem(context)
    candidate = CandidateDecision(value=plan)
    result = InventoryEvaluationExperiment(context).evaluate(problem, candidate)
    return candidate, result


def test_hand_calculated_plan_cost_is_four():
    candidate, result = evaluate((1, 1))

    # Period 0: inventory 1 + production 1 meets demand 2; cost 2.
    # Period 1: inventory 0 + production 1 meets demand 1; cost 2.
    assert result.status is EvaluationStatus.SUCCESS
    assert result.candidate is candidate
    assert result.objective_values == (4,)
    assert result.feasible is None
    assert result.constraint_results == ()


def test_zero_production_plan_costs_ten_due_to_shortage():
    _, result = evaluate((0, 0))

    assert result.status is EvaluationStatus.SUCCESS
    assert result.objective_values == (10,)
    assert result.feasible is None
    assert result.constraint_results == ()


def test_inventory_state_carries_between_periods_and_holding_is_charged():
    context = make_context(
        initial_inventory=2,
        demand=(1, 0),
        production_cost=0,
        holding_cost=3,
        shortage_penalty=100,
    )
    _, result = evaluate((0, 0), context=context)

    # Ending inventory is 1 in each period, so holding cost is 3 + 3.
    assert result.objective_values == (6,)


def test_terminal_inventory_is_charged_as_final_period_holding_cost():
    context = make_context(
        initial_inventory=0,
        demand=(0,),
        production_cost=2,
        holding_cost=3,
        shortage_penalty=5,
    )
    _, result = evaluate((2,), context=context)

    # Production costs 4; ending inventory 2 incurs holding cost 6.
    assert result.objective_values == (10,)


def test_repeated_evaluation_is_deterministic_and_state_is_local():
    context = make_context()
    problem = make_problem(context)
    evaluator = InventoryEvaluationExperiment(context)
    candidate = CandidateDecision(value=(1, 1))

    first = evaluator.evaluate(problem, candidate)
    second = evaluator.evaluate(problem, candidate)

    assert first == second
    assert first.objective_values == (4,)


@pytest.mark.parametrize(
    "plan",
    [
        None,
        (1,),
        (1, 1, 1),
        [1, 1],
        (-1, 2),
        (1, -1),
        (1.5, 1),
        (True, 1),
        "11",
    ],
)
def test_malformed_production_plan_returns_failed_result(plan):
    candidate, result = evaluate(plan)

    assert result.candidate is candidate
    assert result.status is EvaluationStatus.FAILED
    assert result.feasible is None
    assert result.objective_values == ()
    assert result.constraint_results == ()


def test_decision_space_rejects_wrong_horizon_and_invalid_quantities():
    decision_space = InventoryDecisionSpace(horizon=2)

    assert decision_space.is_representable(CandidateDecision((0, 1)))
    assert not decision_space.is_representable(CandidateDecision((0,)))
    assert not decision_space.is_representable(CandidateDecision((0, -1)))
    assert not decision_space.is_representable(CandidateDecision((0, 1.5)))


def test_unrepresentable_candidate_returns_failed_result():
    context = make_context()
    problem = OptimizationProblem(
        decision_space=InventoryDecisionSpace(horizon=1),
        objectives=(MinimizeCostObjective(),),
    )
    candidate = CandidateDecision((1, 1))

    result = InventoryEvaluationExperiment(context).evaluate(problem, candidate)

    assert result.status is EvaluationStatus.FAILED
    assert result.feasible is None


@pytest.mark.parametrize(
    "overrides",
    [
        {"initial_inventory": -1},
        {"initial_inventory": True},
        {"demand": ()},
        {"demand": [1, 2]},
        {"demand": (1, -1)},
        {"demand": (1, True)},
        {"production_cost": -1},
        {"holding_cost": math.inf},
        {"shortage_penalty": math.nan},
        {"production_cost": True},
    ],
)
def test_invalid_fixed_context_is_rejected_at_construction(overrides):
    with pytest.raises(ValueError):
        make_context(**overrides)


def test_wrong_objective_count_returns_failed_result():
    context = make_context()
    problem = OptimizationProblem(
        decision_space=InventoryDecisionSpace(len(context.demand)),
        objectives=(),
    )
    candidate = CandidateDecision((1, 1))

    result = InventoryEvaluationExperiment(context).evaluate(problem, candidate)

    assert result.status is EvaluationStatus.FAILED
    assert result.feasible is None


def test_evaluator_returns_cost_without_owning_optimization_direction():
    context = make_context()
    problem = make_problem(context, objective=MaximizeCostObjective())
    candidate = CandidateDecision((1, 1))

    result = InventoryEvaluationExperiment(context).evaluate(problem, candidate)

    # Evaluation computes the cost; objective direction belongs to the optimizer.
    assert result.status is EvaluationStatus.SUCCESS
    assert result.objective_values == (4,)
    assert result.feasible is None


def test_evaluate_rejects_problem_with_constraints():
    """The inventory evaluator does not support constrained problems."""

    class TestConstraint:
        @property
        def name(self) -> str:
            return "test_constraint"

        def is_satisfied(self, candidate: CandidateDecision) -> bool:
            raise AssertionError(
                "The inventory evaluator must reject constraints "
                "without evaluating them."
            )

    context = make_context()
    problem = OptimizationProblem(
        decision_space=InventoryDecisionSpace(horizon=2),
        objectives=(MinimizeCostObjective(),),
        constraints=(TestConstraint(),),
    )
    candidate = CandidateDecision(value=(1, 1))

    result = InventoryEvaluationExperiment(context).evaluate(problem, candidate)

    assert result.candidate is candidate
    assert result.status is EvaluationStatus.FAILED
    assert result.feasible is None
    assert result.objective_values == ()
    assert result.constraint_results == ()
