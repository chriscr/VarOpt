from varopt import CandidateDecision, OptimizationProblem


class SimpleDecisionSpace:
    """Minimal test-only decision space."""

    def is_representable(self, candidate: CandidateDecision) -> bool:
        return isinstance(candidate.value, int) and candidate.value >= 0


def test_candidate_preserves_domain_decision():
    candidate = CandidateDecision(value=42)

    assert candidate.value == 42


def test_decision_space_controls_representability():
    decision_space = SimpleDecisionSpace()

    assert decision_space.is_representable(
        CandidateDecision(value=42)
    )
    assert not decision_space.is_representable(
        CandidateDecision(value=-1)
    )


def test_optimization_problem_contains_decision_space():
    decision_space = SimpleDecisionSpace()
    problem = OptimizationProblem(decision_space=decision_space)

    assert problem.decision_space is decision_space