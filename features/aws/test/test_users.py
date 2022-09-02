from helper.tests.users import users

def test_users(client, aws):
     users(client, "admin")
