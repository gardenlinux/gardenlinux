"""
Ref: SRG-OS-000590-GPOS-00110

Verify the operating system is configured to disable accounts when the accounts
are no longer associated to a user.
"""

import pytest


@pytest.mark.security_id(263650)
def test_disastig_00110():
    """Account expiration enforcement via pam_unix is checked in test_disastig_00170.py."""
    pytest.skip(reason="covered by test_disastig_00170.py")
