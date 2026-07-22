"""
Ref: SRG-OS-000458-GPOS-00203

Verify the operating system generates audit records when
successful/unsuccessful attempts to access security objects occur.
"""

import pytest


@pytest.mark.security_id(203759)
def test_disastig_00203():
    """Audit of security object access is covered elsewhere."""
    pytest.skip(reason="covered by test_disastig_00089.py")
