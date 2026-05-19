import pytest

"""
Ref: SRG-OS-000120-GPOS-00061, SRG-OS-000329-GPOS-00128

Verify the operating system uses SHA512 as the password hashing algorithm
and automatically locks an account after three consecutive invalid logon
attempts.
"""


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-login-defs-encrypt"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="SHA512 password hashing is configured by disaSTIGmedium"
)
def test_login_defs_encrypt_method_is_sha512(parse_file) -> None:
    config = parse_file.parse("/etc/login.defs", format="spacedelim")
    assert config["ENCRYPT_METHOD"] == "SHA512", (
        f"stigcompliance: ENCRYPT_METHOD in /etc/login.defs is "
        f"{config['ENCRYPT_METHOD']!r}, expected 'SHA512'"
    )


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGlow-config-security-faillock"])
@pytest.mark.feature(
    "disaSTIGlow", reason="faillock deny threshold is configured by disaSTIGlow"
)
def test_faillock_deny_is_3(parse_file) -> None:
    config = parse_file.parse("/etc/security/faillock.conf", format="keyval")
    assert (
        config["deny"] == "3"
    ), f"stigcompliance: deny in /etc/security/faillock.conf is {config['deny']!r}, expected '3'"
