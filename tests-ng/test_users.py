import os
import pwd
import stat

import pytest

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


def test_root_home_permissions():
    mode = os.stat("/root").st_mode
    perm = stat.S_IMODE(mode)
    assert perm == 0o700, f"/root has incorrect permissions: {oct(perm)}"


@pytest.mark.feature("not _dev")
def test_no_extra_home_directories(expected_users):
    if os.path.islink("/home"):
        return
    entries = os.listdir("/home")
    unexpected = [e for e in entries if e not in expected_users]
    assert not unexpected, f"Unexpected entries in /home: {entries}"


@pytest.mark.booted
@pytest.mark.root(reason="Using sudo comamnd to check the access")
def test_users_sudo_capability(expected_users, user: User):
    for entry in pwd.getpwall():
        if (entry.pw_name == "root") or (entry.pw_name in expected_users):
            assert user.is_user_sudo(
                entry.pw_name
            ), f"User: {entry.pw_name} doesn't have sudo permission"
        else:
            assert not user.is_user_sudo(
                entry.pw_name
            ), f"System User {entry.pw_name} has sudo permission"


def test_available_regular_users(get_regular_users, expected_users):
    allowed_users = ["dev", "nobody"] + list(expected_users)
    assert (
        any(user not in allowed_users for user in get_regular_users),
    ), f"Unexpected user account found in /etc/passwd, {user}"
