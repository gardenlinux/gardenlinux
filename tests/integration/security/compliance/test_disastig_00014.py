"""
Ref: SRG-OS-000033-GPOS-00014

Verify the operating system implements DoD-approved encryption to protect the
confidentiality of remote access sessions.
"""

import pytest


@pytest.mark.security_id(203603)
def test_disastig_00014():
    """Encryption for remote access sessions is covered elsewhere."""
    pytest.skip(reason="covered by test_fips.py")
