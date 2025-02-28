from helper.utils import read_file_remote, execute_remote_command
import pytest


@pytest.mark.security_id(165)
def test_sudoers(client, non_container):
    """
    Validate that we have the necessary %sudo configration entry in sudoers.
    Note: we do not use wheel, but instead the sudo group.
    """
    # Ensure we have sudo permissions.
    client._default_to_sudo = True
    output = execute_remote_command(client, "getent group sudo")
    assert output.split(":")[0] == 'sudo', "Group 'sudo' is missing!"

    sudoers = read_file_remote(client,
                               file="/etc/sudoers",
                               remove_comments=True,
                               remove_newlines=True)
    # Drop sudo permissions.
    client._default_to_sudo = False
    _ = [config for config in sudoers if '%sudo' in config]
    assert len(_) == 1, "Missing sudo configuration in '/etc/sudoers'!"
