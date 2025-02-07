from helper.tests.password_shadow import password_shadow
from helper.utils import execute_remote_command
import pytest


@pytest.mark.security_id(167)
@pytest.mark.security_id(168)
@pytest.mark.security_id(169)
@pytest.mark.security_id(170)
@pytest.mark.security_id(324)
def test_password_shadow(client):
    """This ensure that not only the passwd and shadow is as expected,
       it also validates that it's entry are consistent. And that's the
       necessary files are set correctly.
    """
    password_shadow(client)
    # Check with -r for read-only. Ensure that we get the output back from
    # both tools.
    assert '' == execute_remote_command(client, "pwck -r", skip_error=True)
    assert '' == execute_remote_command(client, "grpck -r", skip_error=True)
