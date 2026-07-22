"""
Ref: SRG-OS-000058-GPOS-00028

Verify the operating system protects audit information from unauthorized
modification.
"""

import pytest


@pytest.mark.security_id(203617)
def test_disastig_00028():
    """Audit information protection is covered elsewhere."""
    pytest.skip(reason="covered by test_disastig_00027.py")
