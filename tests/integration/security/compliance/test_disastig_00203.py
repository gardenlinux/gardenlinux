import pytest

"""
Ref: SRG-OS-000458-GPOS-00203

Verify the operating system generates audit records when
successful/unsuccessful attempts to access security objects occur.
"""


@pytest.mark.security_id(203759)
def test_disastig_00203():
    pytest.skip(reason="covered by test_disastig_00089.py")
