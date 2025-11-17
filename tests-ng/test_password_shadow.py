from typing import List

import pytest
from plugins.linux_etc_files import Passwd, Shadow

@pytest.mark.feature("not cis", reason="CIS handles shadow_entries by itself")
def test_shadow_passwords_are_locked(shadow_entries):

def test_shadow_passwords_are_locked(shadow_entries: List[Shadow]):
    """No user in shadow should have a valid password entry and all users are locked."""
    for entry in shadow_entries:
        # Assert that the password field for the given entry is not empty (not invalid)
        assert (
            entry.encrypted_password
        ), f"Empty password field in shadow for {entry.login_name}"

        # Assert whether the first character is a '!' or '*' marking the user as locked.
        assert entry.encrypted_password[0] in [
            "!",
            "*",
        ], f"Unexpected password hash in shadow for {entry.login_name}: {entry.encrypted_password}"


def test_passwd_password_field_is_valid(passwd_entries: List[Passwd]):
    """All passwd entries must use 'x' or '*' in the password field."""
    for entry in passwd_entries:
        assert entry.password in [
            "*",
            "x",
        ], f"Malformed passwd entry for {entry.name}: {entry}"


@pytest.mark.root
@pytest.mark.parametrize("command", ["pwck -r", "grpck -r"])
def test_system_integrity_tools(shell, command):
    """System tools must confirm consistency of passwd and group files."""
    result = shell(command, capture_output=True, ignore_exit_code=True)
    assert result.returncode == 0, f"{command} failed: {result.stderr}"
    assert result.stdout.strip() == "", f"{command} produced unexpected output"
