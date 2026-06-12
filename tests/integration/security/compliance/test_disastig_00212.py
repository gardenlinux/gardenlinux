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
    for syscall in ["unlink", "unlinkat", "rename", "renameat", "rmdir"]:
        assert audit_rule(syscall=syscall, rule_fields=["auid>=1000", "auid!=-1"])
