"""
Ref: SRG-OS-000037-GPOS-00015

Verify the operating system produces audit records containing information to
establish what type of events occurred.
"""

import pytest


@pytest.mark.security_id(203604)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_generated(shell):
    """Verify ausearch -ts recent returns non-empty output."""
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )

    has_output = result.stdout.strip() != ""
    assert has_output, "stigcompliance: no audit events captured"


@pytest.mark.security_id(203604)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_type(shell):
    """Verify ausearch -ts recent output contains a 'type=' field."""
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )

    has_type = "type=" in result.stdout
    assert (
        has_type
    ), "stigcompliance: audit records do not contain event type information"
