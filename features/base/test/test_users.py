import pytest
from helper.tests.users import users
from helper.utils import execute_remote_command, read_file_remote

@pytest.mark.security_id(171)
def test_for_nis(client, non_container):
    """Check if we have no NIS related entries.
       A passwd will then have an entry like this:
       +::::::
    """

    for nssl_file in [ "passwd", "shadow", "group", "gshadow" ]:
       #  Name Service Switch libraries
       nssl = execute_remote_command(client, f"getent {nssl_file}")
       # Assume that when no + is prsent that the split will never return more
       # than one element.
       assert 1 == len(nssl.split("+")), f"NIS entry detected in {nssl_file}!"
      
    nsswitch = read_file_remote(client, "/etc/nsswitch.conf", remove_comments=True)

    # Filtering fileds for nis, nisplus, compat
    assert 0 == len(list(filter(lambda x: 'nis' in x, nsswitch))), "nis found in /etc/nsswitch.conf!"
    assert 0 == len(list(filter(lambda x: 'nisplus' in x, nsswitch))), "nisplus found in /etc/nsswitch.conf!"
    assert 0 == len(list(filter(lambda x: 'compat' in x, nsswitch))), "compat found in /etc/nsswitch.conf!"


@pytest.mark.security_id(164)
def test_for_root(client, non_container):
    """
    Check's that we have a root user present with id 0.

    passwd format, we only care for the frist and third entry.
    0. login name  <---- this is what we need.
    1. optional encrypted password
    2. numerical user ID <---- this is what we need.
    3. numerical group ID
    4. user name or comment field
    5. user home directory
    6. optional user command interpreter
    """
    passwd = read_file_remote(client, "/etc/passwd")

    login_name = 0
    numeric_user_id = 2

    # test if we have only a single user with root and id 0.
    entries_with_root_name = [entry for entry in passwd if 'root' in
                              entry.split(":")[login_name]]
    entries_with_root_id   = [entry for entry in passwd if '0' ==
                              entry.split(":")[numeric_user_id]]
    assert len(entries_with_root_name), 1
    assert len(entries_with_root_id), 1


@pytest.mark.security_id(179)
@pytest.mark.security_id(807)
def test_users(client, non_dev, non_feature_githubActionRunner, non_vhost, non_hyperscalers, non_container, non_ccee):
     users(client)
