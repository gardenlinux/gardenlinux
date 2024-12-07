from helper.tests.password_shadow import password_shadow
from helper.utils import execute_remote_command
import pytest


@pytest.mark.security_id(168)
@pytest.mark.security_id(169)
@pytest.mark.security_id(170)
def test_password_shadow(client):
    password_shadow(client)
    # We're missing some of the default users and that's why pwck will raises an error message?
    assert '' == execute_remote_command(client, "pwck")
