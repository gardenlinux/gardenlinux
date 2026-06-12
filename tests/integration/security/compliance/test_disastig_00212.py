import platform

import pytest

"""
Ref: SRG-OS-000468-GPOS-00212

Verify the operating system generates audit records when
successful/unsuccessful attempts to delete security objects occur.
"""


@pytest.mark.security_id(203766)
@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="auditctl requires a live kernel audit subsystem")
def test_attempts_to_delete_are_audited(audit_rule):
    # unlink, rename, rmdir do not exist as separate syscalls on arm64
    if platform.machine() == "aarch64":
        syscalls = ["unlinkat", "renameat"]
    else:
        syscalls = ["unlink", "unlinkat", "rename", "renameat", "rmdir"]
    for syscall in syscalls:
        assert audit_rule(syscall=syscall, rule_fields=["auid>=1000", "auid!=-1"])
