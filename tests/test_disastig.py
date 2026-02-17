import pytest

from plugins.shell import ShellRunner

@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_audit_reduction_capability(shell: ShellRunner):
    """
    As per DISA STIG requirement, this test verifies the operating system
    provides an audit reduction capability.
    Ref: SRG-OS-000348-GPOS-00136
    """

    output = shell(
        cmd="ausearch -k ssh_login -ts recent | aureport --summary",
        capture_output=True,
    )

    assert (
        output.returncode == 0
    ), f"stigcompliance: audit reduction pipeline failed: {output.stderr}"

    assert (
        "Summary Report" in output.stdout
    ), "stigcompliance: aureport did not generate summary output"
