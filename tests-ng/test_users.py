import os
import pwd
import stat
import shutil

import pytest


def test_service_accounts_have_nologin_shell(get_uid_range):
    for entry in pwd.getpwall():
        if get_uid_range.uid_min <= entry.pw_uid <= get_uid_range.uid_max:
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

@pytest.mark.skipif(sudo_binary is None, reason="sudo does not exist")
@pytest.mark.booted
@pytest.mark.root
def test_sudo_permission_for_users(expected_users, shell: ShellRunner):
    for user in expected_users:
        output = shell(f"sudo -s sudo -l -U {user}", capture_output=True)
        output_lines = output.stdout.strip().splitlines()
        assert (len(output_lines) > 2 and 
            "may run the following commands on" in output_lines[-2], 
            f"User: {user} sudo permission doesn't match requirement : {output_lines[-1]}")

@pytest.mark.booted
@pytest.mark.root
def test_available_users(expected_users, get_uid_range):
    for entry in pwd.getpwall():
        if get_uid_range.uid_min <= entry.pw_uid <= get_uid_range.uid_max:
            assert entry.pw_name in ["dev", "nobody"] + list(expected_users), \
                    f"Unexpected user account found in /etc/passwd: {entry.pw_name}"
