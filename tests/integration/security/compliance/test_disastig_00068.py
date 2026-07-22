"""
Ref: SRG-OS-000134-GPOS-00068

Verify the operating system isolates security functions from nonsecurity
functions.
"""

import pytest


@pytest.mark.security_id(203656)
def test_disastig_00068():
    """Isolation of security from nonsecurity functions is covered elsewhere."""
    pytest.skip(reason="covered by test_disastig_00067.py")
