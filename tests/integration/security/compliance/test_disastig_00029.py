"""
Ref: SRG-OS-000059-GPOS-00029

Verify the operating system protects audit information from unauthorized
deletion.
"""

import pytest


@pytest.mark.security_id(203618)
def test_disastig_00029():
    """Protection of audit information from deletion is covered elsewhere."""
    pytest.skip(reason="covered by test_disastig_00027.py")
