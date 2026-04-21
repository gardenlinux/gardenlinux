import pytest


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.parametrize("pam_config", ["/etc/pam.d/common-password"], indirect=["pam_config"])
def test_common_password_passwdqc_pam_faillock(pam_config):
    """
    Requirements of SRG-OS-000078-GPOS-00046, SRG-OS-000072-GPOS-00040
    """
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
