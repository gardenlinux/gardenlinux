import pytest

"""
Ref: SRG-OS-000134-GPOS-00068

Verify the operating system isolates security functions from nonsecurity
functions.
"""


@pytest.mark.security_id(203656)
def test_disastig_00068():
    pytest.skip(reason="covered by test_disastig_00067.py")
