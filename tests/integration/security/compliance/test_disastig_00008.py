"""
Ref: SRG-OS-000027-GPOS-00008

Verify the operating system limits the number of concurrent sessions to 10
for all accounts and/or account types. A hard maxlogins limit in
/etc/security/limits.conf enforces this restriction.
"""

import pytest


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGlow-config-security-limits"])
@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-limits-maxlogins"])
@pytest.mark.feature(
    "disaSTIGlow", reason="maxlogins limit is configured by disaSTIGlow"
)
@pytest.mark.security_id(203597)
def test_limits_conf_maxlogins_is_10(parse_file) -> None:
    """Verify /etc/security/limits.conf sets a hard maxlogins limit of 10."""
    assert "* hard maxlogins 10" in parse_file.lines("/etc/security/limits.conf")
