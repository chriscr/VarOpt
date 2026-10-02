"""Decision-space boundary."""

from typing import Protocol

from .candidate import CandidateDecision


class DecisionSpace(Protocol):
    """Contract defining which candidate decisions are representable."""

    def is_representable(self, candidate: CandidateDecision) -> bool:
        """Return whether the candidate can be represented in this space."""
        ...
