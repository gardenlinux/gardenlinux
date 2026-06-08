import pytest

"""
Ref: SRG-OS-000426-GPOS-00190

Verify the operating system maintains the confidentiality and integrity of
information during reception.
"""


@pytest.mark.security_id(203751)
def test_disastig_00190():
    pytest.skip(reason="covered by test_disastig_00187.py")
