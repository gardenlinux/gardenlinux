import shutil

import pytest

"""
Ref: SRG-OS-000122-GPOS-00063

Verify the operating system provides an audit reduction capability that
supports on-demand reporting requirements.
"""


def test_audit_reporting_tools_installed(dpkg):
    if dpkg.package_is_installed("auditd"):
        tools = ["aureport", "ausearch"]
        for tool in tools:
            path = shutil.which(tool)
            assert (
                path is not None
            ), f"'{tool}' audit reporting utility is not installed"


@pytest.mark.root(
    "Audit reporting requires root privileges to open /var/log/audit/audit.log"
)
def test_audit_reporting_execution(shell, dpkg):
    if dpkg.package_is_installed("auditd"):
        result = shell("aureport --summary", capture_output=True, ignore_exit_code=True)

        assert (
            "Summary" in result.stdout
        ), f"'aureport' executed but returned an unexpected result: {result.stdout}"
