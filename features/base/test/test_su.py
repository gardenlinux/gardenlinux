import pytest
from helper.utils import read_file_remote as read


@pytest.mark.security_id(166)
def test_su_restriction(client, non_container):
    """
    Validate that we have access to su restircted by default.  The test will
    read the file from `/etc/pam.d/su` and check if it has the configuration
    parameter we exepct.

    A user needs to be configured to be admitted to use `su`. By default, this
    is realized by a specify group, the `wheel` group. We have to ensure that
    this behavior is enabled.
    """

    client._default_to_sudo = True
    pam_file = read(client, file="/etc/pam.d/su", remove_comments=True)
    client._default_to_sudo = False

    assert any(
        "auth" in entry and "pam_wheel.so" in entry for entry in pam_file
    ), "Control value of PAM Module pam_wheel.so must be set to required"
