from helper.tests.users import users

additional_user="azureuser"

def test_users(client, azure):
     users(client=client, additional_user=additional_user, additional_sudo_users=[additional_user])
