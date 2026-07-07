"""
Ref: SRG-OS-000326-GPOS-00126

Verify that the operating system prevents all software from executing at higher
privilege levels than users executing the software.
"""

import pytest


@pytest.mark.security_id(203696)
def test_disastig_00126():
    """Privilege boundary enforcement is covered elsewhere."""
    pytest.skip(reason="covered by test_disastig_00067.py")
