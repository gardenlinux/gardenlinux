"""
Ref: SRG-OS-000042-GPOS-00021

Verify the operating system produces audit records containing the individual
identities of group account users.
"""

import pytest


@pytest.mark.security_id(203610)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_individual_identities(shell):
    """Verify ausearch -ts recent output contains an a0=, a1= or a2= argument field."""
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )
    assert (
        " a0=" in result.stdout or " a1=" in result.stdout or " a2=" in result.stdout
    ), "stigcompliance: audit records do not contain command argument details"
