"""Constraint contract for VarOpt."""

from typing import Protocol

from .candidate import CandidateDecision


class Constraint(Protocol):
    """Contract describing a candidate admissibility condition."""

    @property
    def name(self) -> str:
        """Return the constraint name."""
        ...

    def is_satisfied(self, candidate: CandidateDecision) -> bool:
        """Return whether the candidate satisfies the constraint."""
        ...
