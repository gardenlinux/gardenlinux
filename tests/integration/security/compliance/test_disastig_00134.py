"""
Ref: SRG-OS-000343-GPOS-00134

Verify the operating system takes appropriate action when the audit storage
volume is full. Setting disk_full_action=halt in auditd.conf ensures the
system halts rather than silently dropping audit records.
"""

import pytest

AUDITD_CONF = "/etc/audit/auditd.conf"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGlow-config-audit-auditd-conf"])
@pytest.mark.feature(
    "disaSTIGlow", reason="auditd disk_full_action is configured by disaSTIGlow"
)
@pytest.mark.security_id(203702)
def test_auditd_conf_disk_full_action_is_halt(parse_file) -> None:
    """Verify disk_full_action=halt in auditd.conf (SRG-OS-000343-GPOS-00134)."""
    config = parse_file.parse(AUDITD_CONF, format="keyval")
    assert config["disk_full_action"] == "halt", (
        f"stigcompliance: disk_full_action in {AUDITD_CONF} is "
        f"{config['disk_full_action']!r}, expected 'halt'"
    )
