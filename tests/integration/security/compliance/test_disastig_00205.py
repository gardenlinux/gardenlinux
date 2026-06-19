"""
Ref: SRG-OS-000461-GPOS-00205

Verify the operating system generates audit records when
successful/unsuccessful attempts to access categories of information (e.g.,
classification levels) occur.
"""

import pytest


@pytest.mark.security_id(203760)
def test_disastig_00205():
    """Audit of access to information categories is covered elsewhere."""
    pytest.skip(reason="covered by test_disastig_00210.py")
