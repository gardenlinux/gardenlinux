import pytest

"""
Ref: SRG-OS-000463-GPOS-00207

Verify the operating system generates audit records when
successful/unsuccessful attempts to modify security objects occur.
"""


@pytest.mark.security_id(203762)
def test_disastig_00207():
    pytest.skip(reason="covered by test_disastig_00211.py")
