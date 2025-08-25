import os
import pwd
import pytest
import stat

def test_service_accounts_have_nologin_shell():
    for entry in pwd.getpwall():
        if entry.pw_uid >= 1000:
            continue
        if entry.pw_name in {"root", "sync"}:
            continue
        assert entry.pw_shell in [ "/usr/sbin/nologin", "/bin/false" ], f"User {entry.pw_name} has unexpected shell: {entry.pw_shell}"

def test_root_home_permissions():
    mode = os.stat("/root").st_mode
    perm = stat.S_IMODE(mode)
    assert perm == 0o700, f"/root has incorrect permissions: {oct(perm)}"

@pytest.mark.feature("not _dev")
def test_no_extra_home_directories(expected_users=[]):
    if os.path.islink("/home"):
        return
    entries = os.listdir("/home")
    unexpected = [e for e in entries if e not in expected_users]
    assert not unexpected, f"Unexpected entries in /home: {entries}"
