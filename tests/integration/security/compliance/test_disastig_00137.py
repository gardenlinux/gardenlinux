"""
Ref: SRG-OS-000351-GPOS-00137

Verify the operating system provides an audit reduction capability that
supports after-the-fact investigations of security incidents.
"""

import pytest


@pytest.mark.security_id(203705)
@pytest.mark.feature("log")
def test_disastig_00137():
    """Audit reduction capability is covered elsewhere."""
    pytest.skip(reason="covered by test_disastig_00140.py")
