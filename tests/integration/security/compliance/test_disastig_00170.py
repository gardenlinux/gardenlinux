import pytest

"""
Ref: SRG-OS-000720-GPOS-00170

Verify the operating system is configured to require immediate selection of a
new password upon account recovery for password-based authentication.
"""


@pytest.mark.parametrize(
    "pam_config", ["/etc/pam.d/common-account"], indirect=["pam_config"]
)
def test_password_expiration_checking_pam_module_is_in_use(pam_config):
    """
    man 8 pam_unix:

    The account component performs the task of establishing the status of the
    user's account and password based on the following shadow elements: expire,
    last_change, max_change, min_change, warn_change. In the case of the
    latter, it may offer advice to the user on changing their password or,
    through the PAM_AUTHTOKEN_REQD return, delay giving service to the user
    until they have established a new password.
    """
    results = pam_config.find_entries(
        type_="account",
        control_contains={"success": "1", "new_authtok_reqd": "done"},
        module_contains="pam_unix.so",
    )
    assert len(results) == 1, "pam_unix module should be used for account checking"
