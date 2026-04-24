import pytest
from plugins.parse_file import ParseFile


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.root(reason="requires access to /etc/login.defs")
def test_password_encryption_method_is_sha512(parse_file: ParseFile):
    """
    As per DISA STIG compliance requirements, the operating system must employ
    FIPS-validated cryptographic mechanisms for authenticating users.
    This test verifies that /etc/login.defs is configured to use SHA512 as
    the password encryption method.
    Ref: SRG-OS-000120-GPOS-00061
    """
    config = parse_file.parse("/etc/login.defs", format="spacedelim")

    assert config.get("ENCRYPT_METHOD") == "SHA512", (
        f"stigcompliance: ENCRYPT_METHOD is not SHA512 "
        f"(value={config.get('ENCRYPT_METHOD')!r})"
    )
