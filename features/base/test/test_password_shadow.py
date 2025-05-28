from helper.tests.password_shadow import password_shadow
from helper.utils import execute_remote_command
import pytest


@pytest.mark.security_id(167)
@pytest.mark.security_id(168)
@pytest.mark.security_id(169)
@pytest.mark.security_id(170)
@pytest.mark.security_id(324)
@pytest.mark.parametrize(
    "command, expected_exit_code, expected_output",
    [("pwck -r", 0, ""), ("grpck -r", 0, "")],
)
def test_password_shadow(client, command, expected_exit_code, expected_output):
    """This ensure that not only the passwd and shadow is as expected,
    it also validates that it's entry are consistent. And that's the
    necessary files are set correctly.

    We execute this via the parametrize feature with the -r option. This will
    imply we execute read-only.
    """
    password_shadow(client)
    exit_code, output = execute_remote_command(client, command, skip_error=True, force_sudo=True)
    assert output == ""
    assert exit_code == expected_exit_code
