from helper.tests.users import users

@pytest.mark.security_id(007)
def test_users(client, non_dev, non_feature_githubActionRunner, non_vhost, non_hyperscalers, non_container, non_ccee):
     users(client)
