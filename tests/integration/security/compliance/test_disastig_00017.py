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

    assert (
        "cwd=" in result.stdout
        or "name=" in result.stdout
        or "exe=" in result.stdout
        or "path=" in result.stdout
    ), "stigcompliance: audit records do not contain location (where) information"
