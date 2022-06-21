from helper.tests.users import users

def test_users(client, non_dev, non_feature_github_action_runner):
     users(client)
