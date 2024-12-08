from helper.tests.users import users
import pytest

additional_user="azureuser"

@pytest.mark.security_id(172)
def test_users(client, azure):
     users(client=client, additional_user=additional_user, additional_sudo_users=[additional_user])
