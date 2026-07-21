"""
Ref: SRG-OS-000042-GPOS-00020

Verify the operating system generates audit records containing the full-text
recording of privileged commands.
"""

import pytest


@pytest.mark.security_id(203609)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_full_text_recording(audit_rule, shell):
    """Verify ausearch -ts recent output contains a type=EXECVE record with a0= or a proctitle= field."""
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )
    stdout = result.stdout
    has_full_text = (
        "type=EXECVE" in stdout and " a0=" in stdout
    ) or "proctitle=" in stdout
    assert (
        has_full_text
    ), "stigcompliance: audit records do not contain full-text command recording"
