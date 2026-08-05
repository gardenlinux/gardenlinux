"""
Ref: SRG-OS-000352-GPOS-00140

Verify the operating system provides a report generation capability that
supports after-the-fact investigations of security incidents.
"""

import pytest


@pytest.mark.security_id(203708)
def test_disastig_00140():
    """After-the-fact reporting capability is covered elsewhere."""
    pytest.skip(reason="covered by test_disastig_00063.py")
