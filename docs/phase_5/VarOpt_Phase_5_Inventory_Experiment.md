# VarOpt Phase 5 — Deterministic Inventory Evaluation Experiment

## Status

Initial concrete experiment implementation. The experiment is intentionally local to `varopt.experiments`; it does not add or change a core abstraction.

## Purpose

Demonstrate that VarOpt's existing `Evaluation` boundary and single-objective `Optimizer` can evaluate and compare candidate production plans whose costs depend on deterministic inventory state evolving across a finite, discrete horizon.

The candidate plan is separate from the evolving inventory state. The evaluator receives an immutable fixed context, and all runtime inventory state is local to each evaluation call.

## Model

A plan is a tuple of nonnegative integer production quantities:

\[
u=(u_0,\ldots,u_{T-1})
\]

The immutable context contains initial inventory, a nonempty tuple of nonnegative integer demands, and nonnegative finite production, holding, and shortage cost coefficients. The demand tuple defines the horizon.

For each period, with beginning inventory \(I_t\), demand \(d_t\), and production \(u_t\):

\[
s_t=\max(0,d_t-I_t-u_t)
\]

\[
I_{t+1}=\max(0,I_t+u_t-d_t)
\]

The total cost is:

\[
J(u)=\sum_{t=0}^{T-1}\left(c_pu_t+c_hI_{t+1}+c_ss_t\right)
\]

The ending inventory of every period, including the final period, incurs the holding cost. There is no additional terminal-inventory term and no backorder carryover. Shortage is penalized through the objective and is not represented as a constraint violation.

## Concrete validation case

Context:

- Initial inventory: 1
- Demand: `(2, 1)`
- Production cost: 2 per unit
- Holding cost: 1 per unit of ending inventory per period
- Shortage penalty: 5 per unmet unit

For plan `(1, 1)`, both periods exactly meet demand. Each period costs 2 in production, so the total objective is 4.

For plan `(0, 0)`, each period has one unit of unmet demand and no ending inventory. The total shortage penalty is \(5+5=10\).

The independently calculated expected values are therefore `4` and `10`, respectively. The integration test verifies that the existing optimizer selects `(1, 1)` from a candidate set containing these and other plans.

## Representation and validation

- Production plans are tuples with exactly one quantity per demand period.
- Quantities, demands, and initial inventory are nonnegative integers; booleans are rejected even though Python treats them as integers.
- The concrete decision space checks plan length and quantity types/ranges.
- The evaluator also validates the plan itself and checks the problem's decision-space representability result, because the core optimizer does not perform that check.
- Invalid fixed context is rejected when constructing `InventoryContext` with `ValueError`.
- Invalid candidate plans or unrepresentable candidates return `EvaluationStatus.FAILED`, `feasible=None`, and no objective or constraint results.
- The evaluator returns one cost value and requires exactly one declared objective. It does not enforce objective direction; direction belongs to the existing objective/optimizer contracts. The production/inventory problem should declare minimization for the intended use.
- Successful evaluations return `feasible=None` and no constraint results because this experiment has no constraints.

## Architecture findings

The experiment uses the existing `Evaluation.evaluate(problem, candidate)` boundary and returns the existing `EvaluationResult`. It does not modify `CandidateDecision`, `DecisionSpace`, `OptimizationProblem`, `Objective`, `Constraint`, `CallableEvaluation`, `Optimizer`, or any Phase 4 experiment.

The fixed context is held by the concrete evaluator. Inventory state is a local variable reset from the context on every call, so repeated evaluations are deterministic and independent.

## Validation performed in the implementation workspace

The experiment was validated in the user's Windows working tree.

- Evaluator tests: **29 passed** in 0.21 seconds.
- Optimizer integration tests: **2 passed** in 0.06 seconds.
- Full test suite: **147 passed** in 0.30 seconds.

Environment: Python 3.13.16, pytest 8.4.2. These results were reported from the implementation workspace. The staged changes were also checked with `git diff --cached --check`, which was clean at the time of review.

No commit or push has been made.

## Limitations and open questions

- This is a small deterministic evaluation experiment, not a general simulation framework.
- Candidate generation/search strategies remain outside the evaluator. The existing optimizer only compares the candidates supplied to it.
- There is no backorder model, stochastic demand, dynamic context update, replanning, or dynamic constraint interface.
- Cost coefficients are constrained to nonnegative finite real values; broader numeric-type support has not been demonstrated as necessary.
- The experiment does not establish a need for a reusable dynamic-state abstraction or a new core interface.
