import pytest


@pytest.mark.security_id(1027)
@pytest.mark.booted(reason="Requires booted VM to check SecureBoot via efivars")
@pytest.mark.feature("_trustedboot")
def test_secureboot_enabled(efivars):
    """Ensure SecureBoot is enabled by reading the SecureBoot efivar directly.

    This test reads the raw efivar file for the EFI global variable GUID and
    verifies that the SecureBoot variable's value byte is 1 (enabled). The
    test fails if the efivar file is missing or malformed.
    """
    # EFI_GLOBAL_VARIABLE GUID used for SecureBoot and many other variables
    EFI_GLOBAL_VARIABLE = "8be4df61-93ca-11d2-aa0d-00e098032b8c"

    try:
        data = efivars[EFI_GLOBAL_VARIABLE]["SecureBoot"]
    except KeyError:
        pytest.fail("SecureBoot variable not found in efivars")

    # efivar file format: 4 bytes attributes + value bytes
    if len(data) < 5:
        pytest.fail("SecureBoot efivar content too short or malformed")

    # value byte follows 4-byte attributes
    value = data[4]
    assert value == 1, f"SecureBoot is not enabled (value={value})"
