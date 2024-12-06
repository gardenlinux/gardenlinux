from helper.tests.users import users
import pytest


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
