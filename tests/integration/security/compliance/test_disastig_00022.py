import pytest

"""
Ref: SRG-OS-000043-GPOS-00022

Verify the operating system alerts the ISSO and SA (at a minimum) in the event
of an audit processing failure.
"""


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_audit_processing_failures(shell):
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )

    assert "audit" in result.stdout and (
        "fail" in result.stdout
        or "error" in result.stdout
        or "lost=" in result.stdout
        or "backlog" in result.stdout
    ), "stigcompliance: audit records do not indicate alerting or detection of audit processing failures"
