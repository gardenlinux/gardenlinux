from helper.tests.users import users
import pytest

additional_user = "azureuser"


def test_users(client, azure):
    """
    AZR injects via cloud-init a user. The default username is azureuser and we
    have to make sure that's present. With this, we ensure that the user
    fulfill the security requirements.
    """
    users(client=client,
          additional_user=additional_user,
          additional_sudo_users=[additional_user])
