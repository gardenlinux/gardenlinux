import os
import pwd
import stat
import shutil
from plugins.shell import ShellRunner

users = {
    # feature: additional_user, sudo access
    "vhost": { "username": "libvirt-qemu", "sudo_user": False },
    "ali": { "username": "admin", "sudo_user": True },
    "aws": { "username": "admin", "sudo_user": True },
    "azure": { "username": "azureuser", "sudo_user": True },
    "gcp": { "username": "gardenlinux", "sudo_user": True },
    "openstackbaremetal": { "username": "admin", "sudo_user": True }
}

sudo_binary = shutil.which("sudo")

import pytest


def test_service_accounts_have_nologin_shell():
    for entry in pwd.getpwall():
        if entry.pw_uid >= 1000:
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
@pytest.mark.parametrize(
    "user", [pytest.param(users[feature], marks=pytest.mark.feature(feature)) for feature in users]
)
def test_sudo_permission_for_users(user, shell: ShellRunner):
    output = shell(f"sudo -s sudo -l -U {user['username']}", capture_output=True, ignore_exit_code=True)

    output_lines = []
    for line in output.stdout.split("\n"):
        output_lines.append(line)

    sudo_access = False
    if len(output_lines) > 3:
        if "may run the following commands on" in output_lines[-2]:
            sudo_access = True
    assert sudo_access == user['sudo_user'], f"User: {user['username']} sudo permission doesn't match requirement : {output_lines[-1]}"

@pytest.mark.booted
@pytest.mark.root
@pytest.mark.parametrize(
    "user", [pytest.param(users[feature], marks=pytest.mark.feature(feature)) for feature in users]
)
def test_available_users(user):
    for entry in pwd.getpwall():
        if entry.pw_uid >= 1000:
            assert entry.pw_name in ["dev", "nobody", f"{user['username']}"], \
                    f"Unexpected user account found in /etc/passwd: {user['username']}"
