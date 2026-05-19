import pytest

"""
Ref: SRG-OS-000027-GPOS-00008

Verify the operating system limits the number of concurrent sessions to 10
for all accounts and/or account types. A hard maxlogins limit in
/etc/security/limits.conf enforces this restriction.
"""

LIMITS_CONF = "/etc/security/limits.conf"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGlow-config-security-limits"])
@pytest.mark.feature(
    "disaSTIGlow", reason="maxlogins limit is configured by disaSTIGlow"
)
def test_limits_conf_maxlogins_is_10(parse_file) -> None:
    """Verify hard maxlogins 10 in limits.conf (SRG-OS-000027-GPOS-00008)."""
    lines = parse_file.lines(LIMITS_CONF)
    assert any(
        "hard" in line and "maxlogins" in line and "10" in line for line in lines
    ), f"stigcompliance: {LIMITS_CONF} does not contain 'hard maxlogins 10'"
