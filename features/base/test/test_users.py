import pytest
from helper.tests.users import users
from helper.utils import read_file_remote


@pytest.mark.security_id(161)
def test_users(client, non_dev, non_feature_githubActionRunner, non_vhost, non_hyperscalers, non_container, non_ccee):
     users(client)


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

    Containers do not have a passwd file.
    """
    passwd = read_file_remote(client, file="/etc/passwd")

    login_name = 0
    numeric_user_id = 2

    # test if we have only a single user with root and id 0.
    entries_with_root_name = [entry for entry in passwd if 'root' in
                              entry.split(":")[login_name]]
    entries_with_root_id = [entry for entry in passwd
                            if '0' == entry.split(":")[numeric_user_id]]
    assert len(entries_with_root_name), 1
    assert len(entries_with_root_id), 1
