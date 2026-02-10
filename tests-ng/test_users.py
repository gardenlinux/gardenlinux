import os
import pwd

import pytest
from plugins.file import File
from plugins.users import User


def test_service_accounts_have_nologin_shell(regular_user_uid_range):
    for entry in pwd.getpwall():
        if entry.pw_uid in regular_user_uid_range:
            continue
        if entry.pw_name in {"root", "sync"}:
            continue
        assert entry.pw_shell in [
            "/usr/sbin/nologin",
            "/bin/false",
        ], f"User {entry.pw_name} has unexpected shell: {entry.pw_shell}"


def test_root_home_permissions(file: File):
    assert file.has_mode("/root", "0700"), f"/root has incorrect permissions"


@pytest.mark.feature("not _dev")
def test_no_extra_home_directories(expected_users, file: File):
    if file.is_symlink("/home"):
        return
    entries = os.listdir("/home")
    unexpected = [e for e in entries if e not in expected_users]
    assert not unexpected, f"Unexpected entries in /home: {entries}"


@pytest.mark.booted
@pytest.mark.root(reason="Using sudo command to check the access")
def test_users_sudo_capability(get_all_users, expected_users, user: User):
    users_with_sudo_capabilities = set(
        [u for u in get_all_users if user.is_user_sudo(u)]
    )
    allowed_sudo_users = set(expected_users) | {"root", "dev"}
    unexpected_sudo_users = users_with_sudo_capabilities - allowed_sudo_users

    assert (
        not unexpected_sudo_users
    ), f"Unexpected sudo capability {unexpected_sudo_users}"


def test_available_regular_users(get_regular_users, expected_users):
    allowed_users = ["dev", "nobody"] + list(expected_users)
    unexpected_user = [user for user in get_regular_users if user not in allowed_users]

    assert (
        not unexpected_user
    ), f"Unexpected user account found in /etc/passwd, {unexpected_user}"
