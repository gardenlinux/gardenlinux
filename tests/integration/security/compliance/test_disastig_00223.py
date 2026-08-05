"""
Ref: SRG-OS-000478-GPOS-00223

Verify the operating system implements NIST FIPS-validated cryptography for the
following: to provision digital signatures, to generate cryptographic hashes,
and to protect unclassified information requiring confidentiality and
cryptographic protection in accordance with applicable federal laws, Executive
Orders, directives, policies, regulations, and standards.
"""

import pytest


@pytest.mark.security_id(203776)
def test_fips():
    """FIPS-validated cryptography is covered elsewhere."""
    pytest.skip(reason="covered by test_fips.py")
