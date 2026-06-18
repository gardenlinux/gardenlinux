import pytest

"""
Ref: SRG-OS-000120-GPOS-00061

Verify the operating system uses mechanisms meeting the requirements of
applicable federal laws, Executive orders, directives, policies, regulations,
standards, and guidance for authentication to a cryptographic module.
"""


@pytest.mark.security_id(203649)
def test_disastig_00061():
    pytest.skip(reason="covered by test_fips.py")
