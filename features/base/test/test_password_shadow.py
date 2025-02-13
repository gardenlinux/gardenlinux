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
    [("sudo -S /usr/sbin/pwck -r", 0, ""), ("sudo -S /usr/sbin/grpck -r", 0, "")],
)
def test_password_shadow(client, command, expected_exit_code, expected_output):
    """This ensure that not only the passwd and shadow is as expected,
    it also validates that it's entry are consistent. And that's the
    necessary files are set correctly.

    We execute this via the parametrize feature with the -r option. This will
    imply we execute read-only.
    """
    password_shadow(client)
    exit_code, output = execute_remote_command(client, command, skip_error=True)
    assert output == """"user 'games': directory '/nonexistent' does not exist
user 'man': directory '/nonexistent' does not exist
user 'lp': directory '/nonexistent' does not exist
user 'news': directory '/nonexistent' does not exist
user 'uucp': directory '/nonexistent' does not exist
user 'www-data': directory '/nonexistent' does not exist
user 'list': directory '/nonexistent' does not exist
user 'irc': directory '/nonexistent' does not exist
pwck: no changes"""
     assert exit_code == expected_exit_code
