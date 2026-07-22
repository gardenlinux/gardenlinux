"""
Ref: SRG-OS-000079-GPOS-00047

Verify the operating system obscures feedback of authentication information
during the authentication process to protect the information from possible
exploitation/use by unauthorized individuals.
"""

import pytest
from plugins.file import File
from plugins.parse_file import ParseFile

PAM_FILES = [
    "/etc/pam.d/common-auth",
    "/etc/pam.d/login",
    "/etc/pam.d/sshd",
]


@pytest.mark.security_id(203635)
@pytest.mark.feature("not container")
@pytest.mark.booted(reason="requires authentication stack")
@pytest.mark.root(reason="required for pam.d checks")
def test_authentication_uses_valid_pam_modules(file: File, parse_file: ParseFile):
    """Verify pam_unix or pam_sss is wired into the PAM auth stack."""
    existing_pam_files = [p for p in PAM_FILES if file.exists(p)]

    assert existing_pam_files, "stigcompliance: no PAM configuration files found"

    assert any(
        ("pam_unix.so" in parse_file.lines(p) or "pam_sss.so" in parse_file.lines(p))
        for p in existing_pam_files
    ), "stigcompliance: no valid PAM authentication modules found"


@pytest.mark.security_id(203635)
@pytest.mark.feature("not container")
@pytest.mark.booted(reason="requires authentication stack")
@pytest.mark.root(reason="required for pam.d checks")
def test_authentication_no_insecure_echo(file: File, parse_file: ParseFile):
    """Verify PAM configs do not enable insecure echo of authentication input."""
    for pam_file in PAM_FILES:
        if not file.exists(pam_file):
            continue

        lines = parse_file.lines(pam_file)

        assert (
            "echo" not in lines
        ), f"stigcompliance: insecure echo option found in {pam_file}"
