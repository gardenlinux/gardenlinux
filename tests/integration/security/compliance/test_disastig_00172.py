"""
Ref: SRG-OS-000392-GPOS-00172

Verify the operating system generates audit records for all activities
performed during nonlocal maintenance and diagnostic sessions by
configuring sudo to log to a dedicated file.
"""

import pytest
from plugins.parse_file import ParseFile

SUDO_LOG_CONFIG = "/etc/sudoers.d/disaSTIG-sudo-log"


@pytest.mark.security_id(203735)
@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-sudoers-sudo-log"])
@pytest.mark.feature("disaSTIGmedium", reason="sudo log file required by DISA STIG")
def test_sudo_logfile_configured(parse_file: ParseFile):
    """Verify sudo is configured to log to /var/log/sudo.log."""
    lines = parse_file.lines(SUDO_LOG_CONFIG)
    assert (
        "Defaults logfile=/var/log/sudo.log" in lines
    ), "stigcompliance: sudo is not configured to log to /var/log/sudo.log"
