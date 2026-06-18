import pytest

"""
Ref: SRG-OS-000472-GPOS-00217

Verify the operating system generates audit records showing starting and ending
time for user access to the system.
"""


@pytest.mark.security_id(203770)
def test_disastig_00217():
    pytest.skip(reason="covered by test_disastig_00214.py")
