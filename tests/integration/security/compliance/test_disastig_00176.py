import pytest

"""
Ref: SRG-OS-000396-GPOS-00176

Verify the operating system implements NSA-approved cryptography to protect
classified information in accordance with applicable federal laws, Executive
Orders, directives, policies, regulations, and standards.
"""


@pytest.mark.security_id(203739)
def test_disastig_00176():
    pytest.skip(reason="covered by test_fips.py")
