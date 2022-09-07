from helper.tests.users import users

def test_users(client, gcp):
     users(client, "gardenlinux")
