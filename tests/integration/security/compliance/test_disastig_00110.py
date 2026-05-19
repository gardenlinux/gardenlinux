import pytest

"""
Ref: SRG-OS-000590-GPOS-00110

Verify the operating system is configured to disable accounts when the accounts
are no longer associated to a user.
"""


def test_disastig_00110():
    """
    pam_unix is responsible for account expiration enforcement
    """
    pytest.skip(reason="covered by test_disastig_00170.py")
