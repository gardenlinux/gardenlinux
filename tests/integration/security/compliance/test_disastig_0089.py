import pytest

"""
Ref: SRG-OS-000239-GPOS-00089
Verify the operating system automatically audits account modification.

Ref: SRG-OS-000240-GPOS-00090
Verify the operating system automatically audits account disabling actions.

Ref: SRG-OS-000241-GPOS-00091
Verify the operating system automatically audits account removal actions.
"""


@pytest.mark.feature("stig")
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
        ), f"No audit rule found for {bin} binary calls"
