import pytest


@pytest.mark.parametrize(
    "pam_config", ["/etc/pam.d/common-auth"], indirect=["pam_config"]
)
@pytest.mark.feature("stig")
def test_stig_common_auth_pam_faillock(pam_config):

    results = pam_config.find_entries(
        type_="auth",
        control_contains="required",
        module_contains="pam_faillock.so",
        arg_contains=["preauth", "silent", "audit", "deny=3", "unlock_time=900"],
    )
    assert (
        len(results) == 1
    ), "Logins should be blocked for 15 minutes after 3 failed attempts (preauth check configured)"

    pam_config.find_entries(
        type_="auth",
        control_contains="default=die",
        module_contains="pam_faillock.so",
        arg_contains=["authfail", "silent", "audit", "deny=3", "unlock_time=900"],
    )
    assert (
        len(results) == 1
    ), "Control value of PAM Module pam_faillock.so must be set to required (postauth action configured)"
