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
@pytest.mark.root(reason="required for pam.d checks")
def test_authentication_uses_valid_pam_modules(file: File, parse_file: ParseFile):
    """
    As per DISA STIG requirement, the operating system must obscure feedback
    of authentication information during the authentication process.

    This test verifies that PAM authentication is configured with standard
    modules (pam_unix or pam_sss).

    Ref: SRG-OS-000079-GPOS-00047
    """

    existing_pam_files = [p for p in PAM_FILES if file.exists(p)]

    assert existing_pam_files, "stigcompliance: no PAM configuration files found"

    assert any(
        ("pam_unix.so" in parse_file.lines(p) or "pam_sss.so" in parse_file.lines(p))
        for p in existing_pam_files
    ), "stigcompliance: no valid PAM authentication modules found"


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="requires authentication stack")
@pytest.mark.root(reason="required for pam.d checks")
def test_authentication_no_insecure_echo(file: File, parse_file: ParseFile):
    """
    As per DISA STIG requirement, the operating system must obscure feedback
    of authentication information during the authentication process.

    This test verifies that no insecure echo configuration exists in PAM files.

    Ref: SRG-OS-000079-GPOS-00047
    """

    for pam_file in PAM_FILES:
        if not file.exists(pam_file):
            continue

        lines = parse_file.lines(pam_file)

        assert (
            "echo" not in lines
        ), f"stigcompliance: insecure echo option found in {pam_file}"
