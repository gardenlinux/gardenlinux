from helper.tests.users import users
import pytest

@pytest.mark.parametrize(
     "additional_user",
     [
          "libvirt-qemu"
     ]
)

def test_users(client, non_dev, non_feature_github_action_runner, additional_user):
     users(client, additional_user)
