from helper.tests.file_content import file_content 
from helper.utils import read_file_remote 
import pytest

@pytest.mark.security_id(328)
@pytest.mark.security_id(329)
@pytest.mark.parametrize(
    "file,args",
    [
        ("/etc/pam.d/common-password", "password required pam_passwdqc.so min=disabled,disabled,12,8,8 passphrase=4 similar=deny retry=5"),
        ("/etc/pam.d/common-password", "password required pam_pwhistory.so use_authtok remember=5 retry=5")
    ]
)


def test_pam_faillock(client, file, args):
    file_content(client, file, args, only_line_match=True)


@pytest.mark.security_id(327)
def test_password_age(client):
    """
       The NIST has change it's default policy onwards regarding setting default password age.
       Instead, it's considered an anti-pattern. NIST SP800-63b 3.1.1.2:
       ...
       6. Verifiers and CSPs SHALL NOT require users to change passwords periodically. However, 
          verifiers SHALL force a change if there is evidence of compromise of the authenticator.
       ... 
       https://pages.nist.gov/800-63-4/sp800-63b/authenticators/#passwordver

       We ensure that we *not* have a password age enabled.
    """
    content = read_file_remote(client, "/etc/login.defs", remove_comments=True)
    assert "PASS_MAX_DAYS\t99999" in content, "Error password age was not set to max value."
