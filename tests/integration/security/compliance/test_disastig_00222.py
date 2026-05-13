import pytest
from plugins.audit import AuditRule
from plugins.parse_file import ParseFile

"""
Ref: SRG-OS-000477-GPOS-00222

Verify the operating system generates audit records for all kernel module load,
unload, and restart actions, and also for all program initiations.
"""


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="audit subsystem required")
@pytest.mark.root(reason="requires access to audit rules")
def test_audit_kernel_module_rules_present(parse_file: ParseFile):
    audit = AuditRule()
    rules = audit.rules

    required_syscalls = ["init_module", "delete_module", "finit_module"]

    missing = [
        syscall
        for syscall in required_syscalls
        if not any(syscall in rule for rule in rules)
    ]

    assert (
        not missing
    ), f"stigcompliance: missing audit rules for kernel module operations: {missing}"
