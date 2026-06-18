import pytest

"""
Ref: SRG-OS-000467-GPOS-00211

Verify the operating system generates audit records when
successful/unsuccessful attempts to delete security levels occur.
"""


@pytest.mark.security_id(203765)
@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="auditctl requires a live kernel audit subsystem")
def test_selinux_runtime_changes_are_audited(audit_rule):
    assert audit_rule(fs_watch_path="/sys/fs/selinux", access_types="wa")


@pytest.mark.security_id(203765)
@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="auditctl requires a live kernel audit subsystem")
def test_changes_to_extended_file_attributes_are_audited(audit_rule):
    for sc in [
        "removexattr",
        "fremovexattr",
        "lremovexattr",
        "setxattr",
        "lsetxattr",
        "fsetxattr",
    ]:
        assert audit_rule(syscall=sc)
