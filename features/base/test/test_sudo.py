import pytest
from helper.utils import read_file_remote, execute_remote_command

@pytest.mark.security_id (165)
def test_sudoers(client, non_container):
    """Validate that we have the necessary .
       Note: we do not use wheel, but instead the sudo group.
    """

    output = execute_remote_command(client, "getent group sudo") 
    assert output.split(":")[0] == 'sudo', "Group 'sudo' is missing!"

    sudoers = read_file_remote(client, "/etc/sudoers", remove_comments=True)
    assert len([config for config in sudoers if '%sudo' in config]) == 1, "Missing sudo configuration in '/etc/sudoers'!"
