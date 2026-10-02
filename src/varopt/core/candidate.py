"""Candidate decision representation."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class CandidateDecision:
    """A proposed decision supplied to the optimization process.

    The actual decision representation is domain-specific and intentionally
    opaque to the VarOpt core.
    """

    value: Any