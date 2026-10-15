
from varopt import (
    CandidateDecision,
    ObjectiveSense,
    OptimizationProblem,
    OptimizationStatus,
    Optimizer,
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


def test_existing_optimizer_selects_lowest_cost_eligible_production_plan():
    context = InventoryContext(
        initial_inventory=1,
        demand=(2, 1),
        production_cost=2,
        holding_cost=1,
        shortage_penalty=5,
    )
    problem = OptimizationProblem(
        decision_space=InventoryDecisionSpace(horizon=len(context.demand)),
        objectives=(MinimizeCostObjective(),),
    )
    candidates = (
        CandidateDecision(value=(0, 0)),
        CandidateDecision(value=(1, 1)),
        CandidateDecision(value=(0, 1)),
        CandidateDecision(value=(1,)),  # Invalid horizon; must be ineligible.
    )

    result = Optimizer(InventoryEvaluationExperiment(context)).optimize(
        problem, candidates
    )

    assert result.status is OptimizationStatus.SUCCESS
    assert result.best_candidate is candidates[1]
    assert result.best_evaluation is not None
    assert result.best_evaluation.objective_values == (4,)
    assert result.best_evaluation.feasible is None


def test_existing_optimizer_reports_no_eligible_candidate_for_invalid_plans():
    context = InventoryContext(
        initial_inventory=1,
        demand=(2, 1),
        production_cost=2,
        holding_cost=1,
        shortage_penalty=5,
    )
    problem = OptimizationProblem(
        decision_space=InventoryDecisionSpace(horizon=len(context.demand)),
        objectives=(MinimizeCostObjective(),),
    )

    result = Optimizer(InventoryEvaluationExperiment(context)).optimize(
        problem,
        (CandidateDecision(value=(-1, 1)), CandidateDecision(value=(1,))),
    )

    assert result.status is OptimizationStatus.NO_ELIGIBLE_CANDIDATE
    assert result.best_candidate is None
    assert result.best_evaluation is None