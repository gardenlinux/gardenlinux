import pytest

"""
Ref: SRG-OS-000477-GPOS-00222

Verify the operating system generates audit records for all kernel module load,
unload, and restart actions, and also for all program initiations.
"""


@pytest.mark.security_id(203775)
@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="audit subsystem required")
@pytest.mark.root(reason="requires access to audit rules")
def test_audit_kernel_module_load_rules_present(audit_rule):
    for syscall in ["init_module", "finit_module"]:
        assert audit_rule(syscall=syscall, rule_fields=["auid>=1000", "auid!=-1"])


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="audit subsystem required")
@pytest.mark.root(reason="requires access to audit rules")
def test_audit_kernel_module_delete_rules_present(audit_rule):
    assert audit_rule(syscall="delete_module", rule_fields=["auid>=1000", "auid!=-1"])


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="audit subsystem required")
@pytest.mark.root(reason="requires access to audit rules")
def test_audit_kmod_binary_watched(audit_rule):
    assert audit_rule(fs_watch_path="/bin/kmod", access_types="x")


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="audit subsystem required")
@pytest.mark.root(reason="requires access to audit rules")
def test_audit_modprobe_binary_watched(audit_rule):
    assert audit_rule(fs_watch_path="/sbin/modprobe", access_types="x")
