"""
Ref: SRG-OS-000039-GPOS-00017

Verify the operating system produces audit records containing information to
establish where the events occurred.
"""

import pytest


@pytest.mark.security_id(203606)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_location(shell):
    """Verify ausearch -ts recent output contains a cwd=, name=, exe= or path= field."""
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )

    stdout = result.stdout
    has_location = (
        "cwd=" in stdout or "name=" in stdout or "exe=" in stdout or "path=" in stdout
    )
    assert (
        has_location
    ), "stigcompliance: audit records do not contain location (where) information"
