from helper.tests.users import users

additional_user="gardenlinux"

def test_users(client, gcp):
     users(client=client, additional_user=additional_user, additional_sudo_users=[additional_user])
