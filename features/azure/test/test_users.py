from helper.tests.users import users

def test_users(client, azure):
     users(client, "azureuser")
