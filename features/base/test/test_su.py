import pytest
from helper.utils import read_file_remote as read


@pytest.mark.security_id(166)
def test_su_restriction(client, non_container):
    """
    Validate that we have access to su restircted by default.
    """

    client._default_to_sudo = True
    pam_file = read(client, file="/etc/pam.d/su", remove_comments=True)
    client._default_to_sudo = False

    assert any(
            'auth' in entry and 'pam_wheel.so' in entry
            for entry in pam_file), \
        "Control value of PAM Module pam_wheel.so must be set to required"
