import pytest

"""
Ref: SRG-OS-000078-GPOS-00046

Verify the operating system enforces a minimum 15-character password length.
"""


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-pam-common-password"])
@pytest.mark.feature("stig or disaSTIGmedium")
def test_common_password_passwdqc_pam_faillock(pam_config):
    results = pam_config.find_entries(
        type_="password",
        control_contains="required",
        module_contains="pam_passwdqc.so",
        arg_contains=[
            "min=disabled,disabled,15,15,8",
            "passphrase=4",
            "similar=deny",
            "match=7",
            "retry=5",
        ],
    )
    assert (
        len(results) == 1
    ), "User password should conform to password strength requirements"
