import pytest

"""
Ref: SRG-OS-000478-GPOS-00223

Verify the operating system implements NIST FIPS-validated cryptography for the
following: to provision digital signatures, to generate cryptographic hashes,
and to protect unclassified information requiring confidentiality and
cryptographic protection in accordance with applicable federal laws, Executive
Orders, directives, policies, regulations, and standards.
"""


def test_fips():
    pytest.skip(reason="covered by test_fips.py")
