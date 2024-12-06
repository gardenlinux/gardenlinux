from helper.tests.users import users
from helper.utils import execute_remote_command
import pytest

@pytest.mark.security_id(171)
def test_for_nis(client):
    """Check if we have no NIS related entries.
       A passwd will then have an entry like this:
       +::::::
    """
    for nssl_file in [ "passwd", "shadow", "group", "gshadow" ]:
       #  Name Service Switch libraries
       nssl =  execute_remote_command(client, f"getent {nssl_file}")
       assert 1 == len(nssl.split("+")), f"NIS entry detected in {nssl_file}!"
      
    # ope /etc/nsswitch.conf
    nssswitch =  execute_remote_command(client, "cat /etc/nsswitch.conf")
    # filter out comments
    nsswitch_content = [n for n in nssswitch.split("\n") if '#' not in n]
    nsswitch_content.remove("")

    # Filtering fileds for nis, nisplus, compat
    assert 0 == len(list(filter(lambda x: 'nis' in x, nsswitch_content))), "nis found in /etc/nsswitch.conf!"
    assert 0 == len(list(filter(lambda x: 'nisplus' in x, nsswitch_content))), "nisplus found in /etc/nsswitch.conf!"
    assert 0 == len(list(filter(lambda x: 'compat' in x, nsswitch_content))), "compat found in /etc/nsswitch.conf!"

@pytest.mark.security_id(164)
def test_for_root(client):
     (exit_code, output, error) = client.execute_command( "getent passwd", quiet=True)
     assert exit_code == 0, f"no {error=} expected"

     # Remove the empty newline for simple looping.
     passwd = output.split("\n")
     passwd.remove("")

     # passwd format, we only care for the frist and third entry.
     # 0. login name
     # 1. optional encrypted password
     # 2. numerical user ID
     # 3. numerical group ID
     # 4. user name or comment field
     # 5. user home directory
     # 6. optional user command interpreter

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
def test_users(client, non_dev, non_feature_githubActionRunner, non_vhost, non_hyperscalers, non_container, non_ccee):
     users(client)
