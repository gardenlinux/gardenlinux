"""
Ref: SRG-OS-000425-GPOS-00189

Verify the operating system maintains the confidentiality and integrity of
information during preparation for transmission.
"""

import pytest


@pytest.mark.security_id(203750)
def test_disastig_00189():
    """Confidentiality and integrity for transmission prep is covered elsewhere."""
    pytest.skip(reason="covered by test_disastig_00187.py")
