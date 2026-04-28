import pytest

"""
Ref: SRG-OS-000480-GPOS-00225

Verify the operating system prevents the use of dictionary words for passwords.
"""


@pytest.mark.parametrize(
    "pam_config", ["/etc/pam.d/common-password"], indirect=["pam_config"]
)
@pytest.mark.feature("disaSTIGmedium")
def test_dictionary_passwords_are_forbidden(pam_config):
    """
    passwdqc includes built-in lists of a few thousand common English words
    mostly of lengths from 3 to 6

    Ref: https://manpages.debian.org/testing/passwdqc/passwdqc.conf.5.en.html
    """
    results = pam_config.find_entries(
        type_="password",
        control_contains="required",
        module_contains="pam_passwdqc.so",
    )
    assert len(results) == 1, "passwdqc should be required"
