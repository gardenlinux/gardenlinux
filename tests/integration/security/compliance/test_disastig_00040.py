"""
Ref: SRG-OS-000072-GPOS-00040

Verify the operating system requires the change of at least eight of the total
number of characters when passwords are changed.
"""

import pytest


@pytest.mark.security_id(203628)
def test_disastig_00040():
    """Password character change requirement is covered elsewhere."""
    pytest.skip(reason="covered by test_disastig_00046.py")
