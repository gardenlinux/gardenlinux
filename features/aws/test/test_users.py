from helper.tests.users import users

additional_user="admin"

def test_users(client, aws):
     users(client=client, additional_user=additional_user, additional_sudo_users=[additional_user])
