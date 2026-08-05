"""
Ref: SRG-OS-000353-GPOS-00141

Verify the operating system does not alter original content or time ordering of
audit records when it provides an audit reduction capability.
"""

import pytest


@pytest.mark.security_id(203709)
def test_disastig_00141():
    """Audit reduction record-integrity is covered elsewhere."""
    pytest.skip(reason="covered by test_disastig_00142.py")
