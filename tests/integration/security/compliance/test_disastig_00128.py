import pytest

"""
Ref: SRG-OS-000329-GPOS-00128

Verify the operating system automatically locks an account after three
consecutive invalid logon attempts. Setting deny=3 in faillock.conf enforces
this lockout threshold.
"""

FAILLOCK_CONF = "/etc/security/faillock.conf"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGlow-config-security-faillock"])
@pytest.mark.feature(
    "disaSTIGlow", reason="faillock deny threshold is configured by disaSTIGlow"
)
def test_faillock_deny_is_3(parse_file) -> None:
    """Verify deny=3 in faillock.conf (SRG-OS-000329-GPOS-00128)."""
    config = parse_file.parse(FAILLOCK_CONF, format="keyval")
    assert (
        config["deny"] == "3"
    ), f"stigcompliance: deny in {FAILLOCK_CONF} is {config['deny']!r}, expected '3'"
