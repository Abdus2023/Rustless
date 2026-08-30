"""Acceptance helpers for the four-status native evidence boundary."""
from .models import Status


def native_gate_status(*, applicable: bool, execution_evidence: bool, success: bool = False) -> Status:
    """Return a native gate status without treating tool presence as execution evidence."""
    if not applicable:
        return Status.PARTIALLY_VERIFIED
    if not execution_evidence:
        return Status.BLOCKED
    return Status.VERIFIED if success else Status.BLOCKED


def claim_status(*, execution_evidence: bool, success: bool = False) -> Status:
    """Textual claims remain provisional until independently captured native evidence exists."""
    if execution_evidence and success:
        return Status.VERIFIED
    return Status.PROVISIONAL
