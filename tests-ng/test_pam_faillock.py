import pytest


@pytest.mark.parametrize(
    "pam_config", ["/etc/pam.d/common-auth"], indirect=["pam_config"]
)
@pytest.mark.feature("server")
def test_common_auth_pam_faillock(pam_config):

    results = pam_config.find_entries(
        type_="auth",
        control_contains="required",
        module_contains="pam_faillock.so",
        arg_contains=["preauth", "silent", "audit", "deny=5", "unlock_time=900"],
    )
    assert (
        len(results) == 1
    ), "Logins should be blocked for 900 seconds after 5 failed attempts (preauth check configured)"

    pam_config.find_entries(
        type_="auth",
        control_contains="default=die",
        module_contains="pam_faillock.so",
        arg_contains=["authfail", "silent", "audit", "deny=5", "unlock_time=900"],
    )
    assert (
        len(results) == 1
    ), "Control value of PAM Module pam_faillock.so must be set to required (postauth action configured)"


@pytest.mark.parametrize(
    "pam_config", ["/etc/pam.d/common-account"], indirect=["pam_config"]
)
@pytest.mark.feature("server")
def test_common_account_pam_faillock(pam_config):
    results = pam_config.find_entries(
        type_="account", control_contains="required", module_contains="pam_faillock.so"
    )
    assert (
        len(results) == 1
    ), "User account should be validated for its lock status before session starts"


@pytest.mark.parametrize(
    "pam_config", ["/etc/pam.d/common-password"], indirect=["pam_config"]
)
@pytest.mark.feature("server")
def test_common_password_passwdqc_pam_faillock(pam_config):
    results = pam_config.find_entries(
        type_="password",
        control_contains="required",
        module_contains="pam_passwdqc.so",
        arg_contains=[
            "min=disabled,disabled,12,8,8",
            "passphrase=4",
            "similar=deny",
            "retry=5",
        ],
    )
    assert (
        len(results) == 1
    ), "User password should conform to password strength requirements"


@pytest.mark.parametrize(
    "pam_config", ["/etc/pam.d/common-password"], indirect=["pam_config"]
)
@pytest.mark.feature("server")
def test_common_password_pwhistory_pam_faillock(pam_config):
    results = pam_config.find_entries(
        type_="password",
        control_contains="required",
        module_contains="pam_pwhistory.so",
        arg_contains=["use_authtok", "remember=5", "retry=5"],
    )
    assert len(results) == 1, "Last 5 user passwords should not be reused"
