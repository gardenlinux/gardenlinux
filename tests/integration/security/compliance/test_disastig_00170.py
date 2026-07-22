"""
Ref: SRG-OS-000720-GPOS-00170

Verify the operating system is configured to require immediate selection of a
new password upon account recovery for password-based authentication.
"""

import pytest


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-pam-common-account"])
@pytest.mark.parametrize(
    "pam_config", ["/etc/pam.d/common-account"], indirect=["pam_config"]
)
@pytest.mark.security_id(263654)
def test_password_expiration_checking_pam_module_is_in_use(pam_config):
    """Verify pam_unix.so account entry with success=1 and new_authtok_reqd=done is in /etc/pam.d/common-account."""
    results = pam_config.find_entries(
        type_="account",
        control_contains={"success": "1", "new_authtok_reqd": "done"},
        module_contains="pam_unix.so",
    )
    assert len(results) == 1, "pam_unix module should be used for account checking"
