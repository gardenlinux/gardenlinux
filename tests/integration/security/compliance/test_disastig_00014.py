import pytest

"""
Ref: SRG-OS-000033-GPOS-00014

Verify the operating system implements DoD-approved encryption to protect the
confidentiality of remote access sessions.
"""


@pytest.mark.security_id(203603)
def test_disastig_00014():
    pytest.skip(reason="covered by test_fips.py")
