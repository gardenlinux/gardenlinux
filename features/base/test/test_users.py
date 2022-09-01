from helper.tests.users import users

def test_users(client, non_dev, non_feature_github_action_runner, non_vhost, non_aws, non_azure, non_ali, non_gcp):
     users(client)
