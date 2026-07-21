"""
Ref: SRG-OS-000038-GPOS-00016

Verify the operating system produces audit records containing information to
establish when (date and time) the events occurred.
"""

import pytest


@pytest.mark.security_id(203605)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_timestamp(shell):
    """Verify ausearch -ts recent output contains 'time->' or 'audit(' timestamps."""
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )
    has_timestamp = "time->" in result.stdout or "audit(" in result.stdout
    assert (
        has_timestamp
    ), "stigcompliance: audit records do not contain timestamp information"
