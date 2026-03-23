import pytest
from plugins.shell import ShellRunner


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_generated(shell: ShellRunner):
    """
    As per DISA STIG requirement, the operating system must produce audit
    records containing information to establish what type of events occurred.
    This test verifies that audit records are being generated and 
    when (date and time) the events occurred.
    Ref: SRG-OS-000037-GPOS-00015
         SRG-OS-000038-GPOS-00016
    """
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )

    assert result.stdout.strip() != "", "stigcompliance: no audit events captured"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_type(shell: ShellRunner):
    """
    As per DISA STIG requirement, the operating system must produce audit
    records containing information to establish what type of events occurred.
    This test verifies that audit records are being generated and 
    when (date and time) the events occurred.
    Ref: SRG-OS-000037-GPOS-00015
         SRG-OS-000038-GPOS-00016
    """
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )

    assert (
        "type=" in result.stdout
    ), "stigcompliance: audit records do not contain event type information"

@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_timestamp(shell: ShellRunner):
    """
    As per DISA STIG requirement, the operating system must produce audit
    records containing information to establish what type of events occurred.
    This test verifies that audit records are being generated and 
    when (date and time) the events occurred.
    Ref: SRG-OS-000037-GPOS-00015
         SRG-OS-000038-GPOS-00016
    """
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )
    assert ("time->" in result.stdout or "audit(" in result.stdout), (
        "stigcompliance: audit records do not contain timestamp information"
    )
