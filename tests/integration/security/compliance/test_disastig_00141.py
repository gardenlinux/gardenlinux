import pytest

"""
Ref: SRG-OS-000353-GPOS-00141

Verify the operating system does not alter original content or time ordering of
audit records when it provides an audit reduction capability.
"""


@pytest.mark.security_id(203709)
def test_disastig_00141():
    pytest.skip(reason="covered by test_disastig_00142.py")
