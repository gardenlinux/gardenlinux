"""
Ref: SRG-OS-000043-GPOS-00022

Verify the operating system alerts the ISSO and SA (at a minimum) in the event
of an audit processing failure.
"""

import pytest


@pytest.mark.security_id(203611)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_audit_processing_failures(shell):
    """Verify ausearch -ts recent output mentions 'audit' together with fail/error/lost=/backlog."""
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )

    stdout = result.stdout
    has_failures = "audit" in stdout and (
        "fail" in stdout
        or "error" in stdout
        or "lost=" in stdout
        or "backlog" in stdout
    )
    assert has_failures, "stigcompliance: audit records do not indicate alerting or detection of audit processing failures"
