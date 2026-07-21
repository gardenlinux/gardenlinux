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
    stdout = result.stdout
    has_source = (
        "auid=" in stdout
        or "uid=" in stdout
        or "ses=" in stdout
        or "comm=" in stdout
        or "exe=" in stdout
    )
    assert has_source, "stigcompliance: audit records do not contain source information"
