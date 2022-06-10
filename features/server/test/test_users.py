from helper.tests.users import users

def test_users(client, non_dev):
     users(client)
