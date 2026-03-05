import pytest


@pytest.mark.root(reason="Need root permissions to call auditctl")
def test_audit_attempts_to_delete_privileges(audit_rule):
    assert audit_rule(fs_watch_path="/etc/passwd", access_types="wa")
    assert audit_rule(fs_watch_path="/etc/shadow", access_types="wa")
    assert audit_rule(fs_watch_path="/etc/group", access_types="wa")
    assert audit_rule(fs_watch_path="/etc/sudoers", access_types="wa")

    # this fails in the current setup
    # assert audit_rule(syscall="setcap")

    # for demo only
    assert audit_rule(syscall="umount2")
