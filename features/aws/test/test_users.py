from helper.tests.users import users
import pytest

additional_user="admin"

@pytest.mark.security_id(172)
def test_users(client, aws):
     users(client=client, additional_user=additional_user, additional_sudo_users=[additional_user])
