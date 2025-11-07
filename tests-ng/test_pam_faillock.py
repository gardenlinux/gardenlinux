import pytest


@pytest.mark.feature("server")
def test_common_auth_pam_faillock(file_content):
    file_content.check_lines(
        "/etc/pam.d/common-auth",
        [
            "auth required pam_faillock.so preauth silent audit deny=5 unlock_time=900",
            "auth [default=die] pam_faillock.so authfail silent audit deny=5 unlock_time=900",
        ],
    )


@pytest.mark.feature("server")
def test_common_account_pam_faillock(file_content):
    assert file_content.check_line(
        "/etc/pam.d/common-account", "account required pam_faillock.so"
    )


@pytest.mark.feature("server")
def test_common_password_pam_faillock(file_content):
    assert file_content.check_lines(
        "/etc/pam.d/common-password",
        [
            "password required pam_passwdqc.so min=disabled,disabled,12,8,8 passphrase=4 similar=deny retry=5",
            "password required pam_pwhistory.so use_authtok remember=5 retry=5",
        ],
    )
