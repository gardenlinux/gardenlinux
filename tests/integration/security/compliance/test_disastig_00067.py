"""
Ref: SRG-OS-000132-GPOS-00067

Verify the operating system separates user functionality (including user
interface services) from operating system management functionality.
"""

import pwd

import pytest

SETUID_BINARIES_ALLOWLIST = {
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


@pytest.mark.security_id(203655)
def test_only_root_user_has_uid_zero():
    """Verify only the root account has UID 0."""
    adm_users = [u.pw_name for u in pwd.getpwall() if u.pw_uid == 0]
    assert adm_users == [
        "root"
    ], f"only root user should have uid 0, instead {adm_users} found"


@pytest.mark.security_id(203655)
@pytest.mark.feature("not lima")
def test_only_setuid_binaries_from_the_list_are_allowed(exposed_setuid_binaries):
    """Verify only allowlisted setuid binaries are exposed."""
    if exposed_setuid_binaries:
        diff = exposed_setuid_binaries - SETUID_BINARIES_ALLOWLIST["default"]
        assert (
            not diff
        ), f"unexpected setuid binaries with too broad exec permissions: {exposed_setuid_binaries=} {diff=}"


@pytest.mark.security_id(203655)
@pytest.mark.feature("lima")
def test_only_lima_setuid_binaries_from_the_list_are_allowed(exposed_setuid_binaries):
    """Verify only allowlisted setuid binaries (incl. lima additions) are exposed."""
    if exposed_setuid_binaries:
        diff = exposed_setuid_binaries - (
            SETUID_BINARIES_ALLOWLIST["default"] | SETUID_BINARIES_ALLOWLIST["lima"]
        )
        assert (
            not diff
        ), f"unexpected setuid binaries with too broad exec permissions: {exposed_setuid_binaries=} {diff=}"
