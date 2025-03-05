import pytest
from helper.utils import read_file_remote


@pytest.mark.security_id(166)
def test_su_restriction(client, non_container):
    """
    Validate that we have access to su restircted by default.
    """

    pam_configuration = read_file_remote(client,
                                         file="/etc/pam.d/su",
                                         remove_comments=True)

    assert any('auth' in entry and 'pam_wheel.so' in entry for entry in pam_configuration), "Error pam_wheel.so not set as PAM module!"
