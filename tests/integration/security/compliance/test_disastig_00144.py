"""
Ref: SRG-OS-000356-GPOS-00144

Verify the operating system synchronizes internal information system clocks to
the authoritative time source when the time difference is greater than one
second.
"""

import pytest


@pytest.mark.security_id(203712)
def test_disastig_00144():
    """Clock synchronization tolerance is covered elsewhere."""
    pytest.skip(reason="covered by test_disastig_00143.py")
