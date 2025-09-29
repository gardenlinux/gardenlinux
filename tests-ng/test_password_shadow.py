import os

import pytest


def test_shadow_passwords_are_locked(shadow_entries):
    """No user in shadow should have a valid password hash."""
    for entry in shadow_entries:
        pw = entry["passwd"]
        assert pw and pw[0] in [
            "*",
            "!",
        ], f"Unexpected password hash in shadow for {entry['user']}: {pw}"


def test_passwd_password_field_is_valid(passwd_entries):
    """All passwd entries must use 'x' or '*' in the password field."""
    for entry in passwd_entries:
        pw = entry["passwd"]
        assert pw in ["*", "x"], f"Malformed passwd entry for {entry['user']}: {pw}"


@pytest.mark.root
@pytest.mark.parametrize("command", ["pwck -r", "grpck -r"])
def test_system_integrity_tools(shell, command):
    """System tools must confirm consistency of passwd and group files."""
    # Skip test if unable to access the files (e.g. running without root permissions)
    if not os.access("/etc/shadow", os.R_OK) or not os.access("/etc/gshadow", os.R_OK):
        pytest.skip(f"{command} requires read access to /etc/shadow and /etc/gshadow")

    result = shell(command, capture_output=True, ignore_exit_code=True)
    assert result.returncode == 0, f"{command} failed: {result.stderr}"
    assert result.stdout.strip() == "", f"{command} produced unexpected output"
