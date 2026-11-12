"""
Ref: SRG-OS-000043-GPOS-00022

Verify the operating system alerts the ISSO and SA (at a minimum) in the event of an audit
processing failure. It is critical for the appropriate personnel to be aware if a system is
at risk of failing to process audit logs as required.
"""

import pytest


@pytest.mark.security_id(203611)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit subsystem must be running")
@pytest.mark.root(reason="required to read audit config")
def test_auditd_action_mail_acct_configured(parse_file):
    """Verify auditd notifies personnel on audit processing failure via action_mail_acct."""
    lines = parse_file.lines("/etc/audit/auditd.conf")
    assert (
        "action_mail_acct = root" in lines
    ), "stigcompliance: action_mail_acct is not configured in auditd.conf"


@pytest.mark.security_id(203611)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit subsystem must be running")
@pytest.mark.root(reason="required to read audit config")
def test_auditd_space_left_action_alerts_personnel(parse_file):
    """Verify auditd alerts personnel when audit storage is at risk of being exhausted."""
    lines = parse_file.lines("/etc/audit/auditd.conf")
    assert (
        "space_left_action = SYSLOG" in lines or "space_left_action = EMAIL" in lines
    ), "stigcompliance: space_left_action must be SYSLOG or EMAIL to alert personnel when audit storage is at risk"
