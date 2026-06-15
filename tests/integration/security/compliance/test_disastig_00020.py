import pytest

"""
Ref: SRG-OS-000042-GPOS-00020

Verify the operating system generates audit records containing the full-text
recording of privileged commands.
"""


@pytest.mark.security_id(203609)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_full_text_recording(audit_rule, shell):
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )
    assert (
        "type=EXECVE" in result.stdout and " a0=" in result.stdout
    ) or "proctitle=" in result.stdout, (
        "stigcompliance: audit records do not contain full-text command recording"
    )
