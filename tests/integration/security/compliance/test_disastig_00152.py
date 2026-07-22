"""
Ref: SRG-OS-000365-GPOS-00152
"""

import pytest


@pytest.mark.security_id(203719)
@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-audit-rules-d-disaSTIG-rules"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="audit rules are configured by disaSTIGmedium"
)
@pytest.mark.booted(reason="requires audit subsystem running")
@pytest.mark.root(reason="required to query audit logs")
def test_enforcement_action_audited(audit_rule) -> None:
    """Verify the operating system audits the enforcement actions used to restrict access associated with changes to the system"""
    assert audit_rule(
        fs_watch_path="/etc/shadow", access_types="wa"
    ), "stigcompliance: no audit rule found watching /etc/shadow for write/append access"
