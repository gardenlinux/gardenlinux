import os
import pathlib
import pwd

import pytest

"""
Ref: SRG-OS-000132-GPOS-00067

Verify the operating system separates user functionality (including user
interface services) from operating system management functionality.

Ref: SRG-OS-000134-GPOS-00068

Verify the operating system isolates security functions from nonsecurity
functions.

Ref: SRG-OS-000326-GPOS-00126

Verify that the operating system prevents all software from executing at higher
privilege levels than users executing the software.
"""

SETUID_BINARIES_WHITELIST = {
    "default": {
        "/usr/bin/chfn",
        "/usr/bin/chsh",
        "/usr/bin/gpasswd",
        "/usr/bin/passwd",
        "/usr/bin/su",
        "/usr/bin/sudo",
        "/usr/bin/sudoedit",
    },
    "lima": {"/usr/bin/fusermount3", "/usr/bin/fusermount"},
}


@pytest.fixture
def exposed_setuid_binaries():
    """
    Returns a set of pathnames of root-owned binaries with setuid bit which are
    also "others"-executable (i.e. binaries that give root privileges to every
    user).
    """
    dirs = [
        "/usr/sbin",
        "/usr/bin",
        "/usr/libexec",
        "/usr/local/sbin",
        "/usr/local/bin",
    ]
    return {
        str(p)
        for d in dirs
        for root, _, files in os.walk(d)
        for p in map(lambda n: pathlib.Path(root) / n, files)
        if p.stat().st_uid == 0  # file belongs to root
        and (m := p.stat().st_mode) & 0o4000  # set‑uid bit present
        and ((m >> 3) & 0o111)  # “others” execute bit set
    }


def test_only_root_user_has_uid_zero():
    adm_users = [u.pw_name for u in pwd.getpwall() if u.pw_uid == 0]
    assert adm_users == [
        "root"
    ], f"only root user should have uid 0, instead {adm_users} found"


@pytest.mark.feature("not lima")
def test_only_whitelisted_setuid_binaries_are_allowed(exposed_setuid_binaries):
    if exposed_setuid_binaries:
        diff = exposed_setuid_binaries - SETUID_BINARIES_WHITELIST["default"]
        assert (
            not diff
        ), f"unexpected setuid binaries with too broad exec permissions: {exposed_setuid_binaries=} {diff=}"


@pytest.mark.feature("lima")
def test_only_whitelisted_lima_setuid_binaries_are_allowed(exposed_setuid_binaries):
    if exposed_setuid_binaries:
        diff = exposed_setuid_binaries - (
            SETUID_BINARIES_WHITELIST["default"] | SETUID_BINARIES_WHITELIST["lima"]
        )
        assert (
            not diff
        ), f"unexpected setuid binaries with too broad exec permissions: {exposed_setuid_binaries=} {diff=}"
