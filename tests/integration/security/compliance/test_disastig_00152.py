import pytest
from plugins.audit import AuditRule


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="requires audit subsystem running")
@pytest.mark.root(reason="required to validate enforcement audit logging")
def test_enforcement_action_audited(audit_rule: AuditRule):
    """
    As per DISA STIG compliance requirement, the operating system must audit the
    enforcement actions used to restrict access associated with changes to the system.
    This test verifies that an audit rule exists watching /etc/shadow for write/append
    access, ensuring enforcement actions on system files are audited.
    Ref: SRG-OS-000365-GPOS-00152
    """
    assert audit_rule(
        fs_watch_path="/etc/shadow", access_types="wa"
    ), "stigcompliance: no audit rule found watching /etc/shadow for write/append access"
