"""
Ref: SRG-OS-000122-GPOS-00063

Verify the operating system provides an audit reduction capability that
supports on-demand reporting requirements.
"""

import shutil

import pytest


@pytest.mark.security_id(203651)
@pytest.mark.feature("log")
def test_audit_reporting_tools_installed():
    """Verify aureport and ausearch are installed."""
    tools = ["aureport", "ausearch"]
    for tool in tools:
        path = shutil.which(tool)
        assert path is not None, f"'{tool}' audit reporting utility is not installed"


@pytest.mark.feature("log")
@pytest.mark.root(
    "Audit reporting requires root privileges to open /var/log/audit/audit.log"
)
@pytest.mark.security_id(203651)
def test_audit_reporting_execution(shell):
    """Verify aureport produces a usable summary."""
    result = shell("aureport --summary", capture_output=True, ignore_exit_code=True)
    has_summary = "Summary" in result.stdout
    assert has_summary, "'aureport' executed but returned an unexpected result"
