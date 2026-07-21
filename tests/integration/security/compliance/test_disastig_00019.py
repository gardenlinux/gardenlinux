"""
SRG-OS-000041-GPOS-00019

Verify the operating system produces audit records containing information to
establish the outcome of the events.
"""

import pytest


@pytest.mark.security_id(203608)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_full_record(shell):
    """Verify ausearch -ts recent output contains a success=yes/no or res=success/failed field."""
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )
    stdout = result.stdout
    has_outcome = (
        "success=yes" in stdout
        or "success=no" in stdout
        or "res=success" in stdout
        or "res=failed" in stdout
    )
    assert has_outcome, "stigcompliance: audit records do not contain outcome (success/failure) information"
