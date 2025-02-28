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

    auth_config = [config for config in pam_configuration if 'auth' in config]
    for entry in auth_config:
        if 'pam_wheel.so' in entry:
            assert 'required pam_wheel.so' in entry, \
              "Error configuration for the pam_wheel.so"
            test_successfully = True

    if not test_successfully:
        assert False, "Error pam_wheel.so not found!"
