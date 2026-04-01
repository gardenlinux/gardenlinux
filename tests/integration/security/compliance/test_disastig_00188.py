import re

import pytest
from plugins.sshd import Sshd


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires sshd effective configuration")
@pytest.mark.root(reason="required to inspect ssh cryptographic configuration")
def test_ssh_strong_cryptography_enforced(sshd: Sshd):
    """
    As per DISA STIG compliance requirement, the operating system must implement
    cryptographic mechanisms to prevent unauthorized disclosure of information
    and/or detect changes to information during transmission.
    This test verifies that SSH is configured with strong cryptographic algorithms
    and does not allow weak or insecure mechanisms.
    Ref: SRG-OS-000424-GPOS-00188
    """

    ciphers = sshd.get_config_section("ciphers") or ""
    macs = sshd.get_config_section("macs") or ""
    kex = sshd.get_config_section("kexalgorithms") or ""

    weak_patterns = [
        r"arcfour",
        r"3des",
        r"cbc",
        r"hmac-md5",
        r"diffie-hellman-group1-sha1",
    ]

    for pattern in weak_patterns:
        assert not re.search(
            pattern, str(ciphers), re.IGNORECASE
        ), f"stigcompliance: weak cipher allowed: {pattern}"

        assert not re.search(
            pattern, str(macs), re.IGNORECASE
        ), f"stigcompliance: weak MAC allowed: {pattern}"

        assert not re.search(
            pattern, str(kex), re.IGNORECASE
        ), f"stigcompliance: weak key exchange algorithm allowed: {pattern}"

    assert (
        ciphers and macs and kex
    ), "stigcompliance: SSH cryptographic mechanisms not explicitly configured"
