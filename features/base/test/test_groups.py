import pytest
from helper.tests.groups import groups 


@pytest.mark.parametrize(
    "group,user",
    [
        ("root", []),
        ("wheel", [])
    ]
)


def test_groups(client, group, user, non_dev):
     groups(client, group, user)
