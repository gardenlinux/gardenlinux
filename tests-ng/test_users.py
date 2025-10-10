import os
import pwd
import stat
import shutil

import pytest


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

@pytest.mark.skipif((shutil.which("sudo")) is None, reason="sudo does not exist")
@pytest.mark.booted
@pytest.mark.root
def test_users_sudo_capability(expected_users, shell: ShellRunner):
    for entry in pwd.getpwall():
        output = shell(f"sudo --list --other-user={entry.pw_name}", capture_output=True)
        output_lines = output.stdout.strip().splitlines()
        if len(output_lines) > 2:
            if (entry.pw_name == "root") or (entry.pw_name in expected_users):
                assert any("may run the following commands on" in line for line in output_lines), f"User: {entry.pw_name} doesn't have sudo permission"
            else:
                assert False, f"System User {entry.pw_name} has sudo permission"


@pytest.mark.booted
@pytest.mark.root
def test_available_users(expected_users, regular_user_uid_range):
    for entry in pwd.getpwall():
        if entry.pw_uid in regular_user_uid_range:
            assert entry.pw_name in ["dev", "nobody"] + list(expected_users), \
                    f"Unexpected user account found in /etc/passwd: {entry.pw_name}"
