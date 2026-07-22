"""
Ref: SRG-OS-000426-GPOS-00190

Verify the operating system maintains the confidentiality and integrity of
information during reception.
"""

import pytest


@pytest.mark.security_id(203751)
def test_disastig_00190():
    """Confidentiality and integrity during reception is covered elsewhere."""
    pytest.skip(reason="covered by test_disastig_00187.py")
