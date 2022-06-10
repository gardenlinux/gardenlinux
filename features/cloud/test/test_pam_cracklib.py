from helper.tests.file_content import file_content
import pytest

@pytest.mark.parametrize(
    "file,args",
    [
        ("/etc/pam.d/common-password", "password required pam_cracklib.so dcredit=-1 ucredit=-1 lcredit=-1 minlen=8 retry=5 reject_username"),
        ("/etc/pam.d/common-password", "password required pam_pwhistory.so use_authtok remember=5 retry=5")
    ]
)


def test_pam_faillock(client, file, args):
    file_content(client, file, args, only_line_match=True)
