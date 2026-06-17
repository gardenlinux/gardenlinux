import pytest

"""
Ref: SRG-OS-000239-GPOS-00089

Verify the operating system automatically audits account modification.
"""


@pytest.mark.security_id(203666)
@pytest.mark.testcov(
    [
        "GL-TESTCOV-disaSTIGmedium-config-audit-rules-d-30-disaSTIG-rules",
        "GL-TESTCOV-disaSTIGmedium-config-audit-rules-d-disaSTIG-rules",
    ]
)
@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="auditctl requires a live kernel audit subsystem")
def test_audit_calling_user_group_related_utilities(audit_rule):
    for bin in [
        "/usr/sbin/visudo",
        "/usr/sbin/chgpasswd",
        "/usr/sbin/chpasswd",
        "/usr/sbin/groupadd",
        "/usr/sbin/groupdel",
        "/usr/sbin/groupmod",
        "/usr/sbin/grpconv",
        "/usr/sbin/grpunconv",
        "/usr/sbin/newusers",
        "/usr/sbin/pwconv",
        "/usr/sbin/pwunconv",
        "/usr/sbin/shadowconfig",
        "/usr/sbin/useradd",
        "/usr/sbin/userdel",
        "/usr/sbin/usermod",
        "/usr/sbin/vipw",
        "/usr/sbin/vigr",
        "/usr/bin/chage",
        "/usr/bin/chfn",
        "/usr/bin/chsh",
        "/usr/bin/gpasswd",
        "/usr/bin/passwd",
    ]:
        assert audit_rule(
            fs_watch_path=bin, access_types="x"
        ), f"No audit rule found for {bin} execution"


@pytest.mark.security_id(203666)
def test_audit_rules_for_logging_attempts_to_delete_privileges():
    pytest.skip(
        reason="covered by test_disastig_00210::test_audit_rules_for_logging_attempts_to_delete_privileges"
    )
