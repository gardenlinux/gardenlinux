"""
Ref: SRG-OS-000462-GPOS-00206

Verify the operating system generates audit records when
successful/unsuccessful attempts to modify privileges occur.
"""

import pytest


@pytest.mark.security_id(203761)
def test_disastig_00206():
    """Audit of privilege modification is covered elsewhere."""
    pytest.skip(reason="covered by test_disastig_00210.py")
