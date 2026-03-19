import pytest
from plugins.shell import ShellRunner

@pytest.mark.feature(
    "not container and not gardener and not lima and not capi and not baremetal"
)
@pytest.mark.booted(reason="requires booted system")
@pytest.mark.root(reason="requires audit operations")
def test_audit_records_contain_valid_identity(shell: ShellRunner):
    """
    As per DISA STIG compliance requirement, its needed to verify the operating 
    system produces audit records containing information to establish the identity 
    of any individual or process associated with the event.
    Ref: SRG-OS-000255-GPOS-00096
    """

    result = shell("ausearch -ts recent")

    assert result.stdout, "stigcompliance: no audit records found"

    lines = result.stdout.splitlines()

    valid_identity_found = False

    for line in lines:
        if (
            "auid=" in line
            and "uid=" in line
            and "pid=" in line
            and "comm=" in line
            and "exe=" in line
            and "auid=4294967295" not in line
        ):
            valid_identity_found = True
            break

    assert valid_identity_found, (
        "stigcompliance: no audit record with valid user identity found"
    )