"""
Ref: SRG-OS-000329-GPOS-00128

Verify the operating system automatically locks an account until the locked
account is released by an administrator when three unsuccessful logon attempts
in 15 minutes are made.
"""

import pytest


@pytest.mark.security_id(203698)
@pytest.mark.feature("disaSTIGmedium")
def test_user_locked_after_unsuccessful_logon_attempts(parse_file):
    """Verify faillock.conf enforces 3 attempts in 900s with admin-only unlock."""
    config = parse_file.parse("/etc/security/faillock.conf", format="keyval")
    assert config["deny"] == "3"
    assert config["fail_interval"] == "900"
    assert config["unlock_time"] == "0"
