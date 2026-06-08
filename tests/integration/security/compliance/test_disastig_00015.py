import pytest

"""
Ref: SRG-OS-000037-GPOS-00015

Verify the operating system produces audit records containing information to
establish what type of events occurred.
"""


@pytest.mark.security_id(203604)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_generated(shell):
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )

    assert result.stdout.strip() != "", "stigcompliance: no audit events captured"


@pytest.mark.security_id(203604)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_type(shell):
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )

    assert (
        "type=" in result.stdout
    ), "stigcompliance: audit records do not contain event type information"
