import pytest

"""
Ref: SRG-OS-000070-GPOS-00038

Verify the operating system enforces password complexity by requiring at least
one lowercase character. Setting lcredit=-1 in pwquality.conf mandates at
least one lowercase letter in every new password.
"""

PWQUALITY_CONF = "/etc/security/pwquality.conf"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGlow-config-security-pwquality"])
@pytest.mark.feature(
    "disaSTIGlow", reason="password quality lcredit is configured by disaSTIGlow"
)
@pytest.mark.security_id(203626)
def test_pwquality_conf_lcredit_is_minus_1(parse_file) -> None:
    """Verify lcredit=-1 in pwquality.conf (SRG-OS-000070-GPOS-00038)."""
    config = parse_file.parse(PWQUALITY_CONF, format="keyval")
    assert (
        config["lcredit"] == "-1"
    ), f"stigcompliance: lcredit in {PWQUALITY_CONF} is {config['lcredit']!r}, expected '-1'"
