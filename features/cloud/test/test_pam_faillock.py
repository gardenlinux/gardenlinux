from helper.tests.file_content import file_content
import pytest

@pytest.mark.parametrize(
    "file,args",
    [
        ("/etc/pam.d/common-auth", "auth required pam_faillock.so preauth silent audit deny=5 unlock_time=900"),
        ("/etc/pam.d/common-auth", "auth [default=die] pam_faillock.so authfail silent audit deny=5 unlock_time=900"),
        ("/etc/pam.d/common-account", "account required pam_faillock.so")
    ]
)


def test_pam_faillock(client, file, args):
    file_content(client, file, args, only_line_match=True)
