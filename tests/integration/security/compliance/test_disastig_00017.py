import pytest

"""
Ref: SRG-OS-000039-GPOS-00017

Verify the operating system produces audit records containing information to
establish where the events occurred.
"""


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_location(shell):
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
