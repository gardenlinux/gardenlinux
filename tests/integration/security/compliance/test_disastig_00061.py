import pytest
from plugins.parse_file import ParseFile


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.root(reason="requires access to /etc/login.defs")
def test_password_encryption_method_is_sha512(parse_file: ParseFile):
    """
    As per DISA STIG compliance requirements, the operating system must employ FIPS
    140-2 approved cryptographic hashing algorithms for all stored passwords.
    This test verifies that /etc/login.defs is configured to use SHA512 for password
    encryption.
    Ref: SRG-OS-000120-GPOS-00061
    """
    config = parse_file.parse("/etc/login.defs", format="spacedelim")
    assert (
        config["ENCRYPT_METHOD"] == "SHA512"
    ), "stigcompliance: ENCRYPT_METHOD in /etc/login.defs must be SHA512"
