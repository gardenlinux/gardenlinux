"""
Ref: SRG-OS-000471-GPOS-00215

Verify the operating system generates audit records for privileged activities
or other system-level access.
"""

import pytest


@pytest.mark.security_id(203768)
def test_disastig_00215():
    """Audit of privileged activities is covered by other tests."""
    pytest.skip(
        reason="covered by test_disastig_00209.py, test_disastig_00210.py, test_disastig_00211.py test_disastig_00220.py test_disastig_00222.py"
    )
