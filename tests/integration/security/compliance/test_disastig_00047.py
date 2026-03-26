import pytest
from plugins.file import File
from plugins.parse_file import ParseFile

PAM_FILES = [
    "/etc/pam.d/common-auth",
    "/etc/pam.d/login",
    "/etc/pam.d/sshd",
]


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="requires authentication stack")
def test_authentication_obscures_password_input(file: File, parse_file: ParseFile):
    """
    As per DISA STIG requirement, the operating system must obscure feedback
    of authentication information during the authentication process.
    This test verifies that PAM authentication is configured with standard
    modules that do not expose password input.
    Ref: SRG-OS-000079-GPOS-00047
    """
    found_valid_auth = False
    for pam_file in PAM_FILES:
        if not file.exists(pam_file):
            continue

        lines = parse_file.lines(pam_file)

        if "pam_unix.so" in lines or "pam_sss.so" in lines:
            found_valid_auth = True

        assert (
            " echo " not in lines
        ), f"stigcompliance: insecure echo option found in {pam_file}"

    assert found_valid_auth, "stigcompliance: no valid PAM authentication modules found"
