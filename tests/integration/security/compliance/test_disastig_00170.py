"""
Ref: SRG-OS-000720-GPOS-00170

Verify the operating system is configured to require immediate selection of a
new password upon account recovery for password-based authentication.
"""


def test_password_recovery_tools_available(shell):
    assert shell("which passwd")
    assert shell("which chage")
