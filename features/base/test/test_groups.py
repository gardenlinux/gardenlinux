import pytest
from helper.tests.groups import groups 

@pytest.mark.security_id(180)
@pytest.mark.parametrize(
    "group,user",
    [
        ("root", []),
        ("wheel", [])
    ]
)


def test_groups(client, group, user, non_dev, non_feature_githubActionRunner, non_container):
     groups(client, group, user)
