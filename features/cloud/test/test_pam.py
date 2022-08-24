from helper.tests.file_content import file_content
import pytest

@pytest.mark.parametrize(
    "file,args",
    [
        ("/etc/pam.d/common-password", "password required pam_passwdqc.so min=disabled,disabled,12,8,8 passphrase=4 similar=deny retry=5"),
        ("/etc/pam.d/common-password", "password required pam_pwhistory.so use_authtok remember=5 retry=5")
    ]
)


def test_pam_faillock(client, file, args):
    file_content(client, file, args, only_line_match=True)
