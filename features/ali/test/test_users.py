from helper.tests.users import users

def test_users(client, ali):
     users(client, "admin")
