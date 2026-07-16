"""
Ref: SRG-OS-000040-GPOS-00018

Verify the operating system produces audit records containing information to
establish the source of the events.
"""

import pytest


@pytest.mark.security_id(203607)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_source(shell):
    """Verify ausearch -ts recent output contains an auid=, uid=, ses=, comm= or exe= field."""
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )
    assert (
        "auid=" in result.stdout
        or "uid=" in result.stdout
        or "ses=" in result.stdout
        or "comm=" in result.stdout
        or "exe=" in result.stdout
    ), "stigcompliance: audit records do not contain source information"
