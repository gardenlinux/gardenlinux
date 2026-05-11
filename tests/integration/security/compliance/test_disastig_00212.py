"""
Ref: SRG-OS-000468-GPOS-00212

Verify the operating system generates audit records when
successful/unsuccessful attempts to delete security objects occur.
"""


def test_attempts_to_delete_are_audited(audit_rule):
    for syscall in ["unlink", "unlinkat", "rename", "renameat", "rmdir"]:
        assert audit_rule(syscall=syscall)
