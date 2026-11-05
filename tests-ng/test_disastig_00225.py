"""
Ref: SRG-OS-000480-GPOS-00225

Verify the operating system prevents the use of dictionary words for passwords.
"""

import pytest


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-pam-common-password"])
@pytest.mark.parametrize(
    "pam_config", ["/etc/pam.d/common-password"], indirect=["pam_config"]
)
@pytest.mark.security_id(203778)
@pytest.mark.feature("disaSTIGmedium")
def test_dictionary_passwords_are_forbidden(pam_config):
    """Verify pam_passwdqc.so is required as a password module in /etc/pam.d/common-password."""
    results = pam_config.find_entries(
        type_="password",
        control_contains="required",
        module_contains="pam_passwdqc.so",
    )
    assert len(results) == 1, "passwdqc should be required"
