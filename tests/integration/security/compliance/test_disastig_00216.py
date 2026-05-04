import pytest
from plugins.audit import AuditRule


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="audit subsystem required to query active rules")
@pytest.mark.root(reason="requires access to audit rules via auditctl")
def test_audit_modprobe_watch_rule_present(audit_rule: AuditRule):
    """
    As per DISA STIG compliance requirements, the audit system must be configured
    to audit the loading and unloading of dynamic kernel modules.
    This test verifies that /sbin/modprobe is watched for execution.
    Ref: SRG-OS-000471-GPOS-00216
    """
    assert audit_rule(
        fs_watch_path="/sbin/modprobe", access_types="x"
    ), "stigcompliance: no audit watch rule for /sbin/modprobe execution"


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="audit subsystem required to query active rules")
@pytest.mark.root(reason="requires access to audit rules via auditctl")
def test_audit_kmod_watch_rule_present(audit_rule: AuditRule):
    """
    As per DISA STIG compliance requirements, the audit system must be configured
    to audit the loading and unloading of dynamic kernel modules.
    This test verifies that /bin/kmod is watched for execution.
    Ref: SRG-OS-000471-GPOS-00216
    """
    assert audit_rule(
        fs_watch_path="/bin/kmod", access_types="x"
    ), "stigcompliance: no audit watch rule for /bin/kmod execution"
