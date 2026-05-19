import pytest

"""
Ref: SRG-OS-000120-GPOS-00061

Verify the operating system uses SHA512 as the password hashing algorithm.
Using a strong hashing algorithm protects stored credentials from offline
dictionary attacks.
"""

LOGIN_DEFS = "/etc/login.defs"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-login-defs-encrypt"])
@pytest.mark.feature("disaSTIGmedium", reason="SHA512 password hashing is configured by disaSTIGmedium")
def test_login_defs_encrypt_method_is_sha512(parse_file) -> None:
    """Verify ENCRYPT_METHOD in /etc/login.defs is SHA512 (SRG-OS-000120-GPOS-00061)."""
    config = parse_file.parse(LOGIN_DEFS, format="spacedelim")
    assert config["ENCRYPT_METHOD"] == "SHA512", (
        f"stigcompliance: ENCRYPT_METHOD in {LOGIN_DEFS} is "
        f"{config['ENCRYPT_METHOD']!r}, expected 'SHA512'"
    )
