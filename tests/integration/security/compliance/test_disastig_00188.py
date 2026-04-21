import re

import pytest
from plugins.sshd import Sshd


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires sshd effective configuration")
@pytest.mark.root(reason="required to inspect ssh cryptographic configuration")
def test_ssh_ciphers_are_strong(sshd: Sshd):
    """
    As per DISA STIG compliance requirement, the operating system must implement
    cryptographic mechanisms to prevent unauthorized disclosure of information
    and/or detect changes to information during transmission.
    This test verifies that SSH is configured with strong cryptographic algorithms
    and does not allow weak or insecure mechanisms.
    Ref: SRG-OS-000424-GPOS-00188
    """
    ciphers = sshd.get_config_section("ciphers") or ""

    assert not re.search(
        r"(arcfour|3des|cbc)", str(ciphers), re.IGNORECASE
    ), "stigcompliance: weak cipher allowed in SSH configuration"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires sshd effective configuration")
@pytest.mark.root(reason="required to inspect ssh cryptographic configuration")
def test_ssh_macs_are_strong(sshd: Sshd):
    """
    As per DISA STIG compliance requirement, the operating system must implement
    cryptographic mechanisms to prevent unauthorized disclosure of information
    and/or detect changes to information during transmission.
    This test verifies that SSH is configured with strong cryptographic algorithms
    and does not allow weak or insecure mechanisms.
    Ref: SRG-OS-000424-GPOS-00188
    """
    macs = sshd.get_config_section("macs") or ""

    assert not re.search(
        r"hmac-md5", str(macs), re.IGNORECASE
    ), "stigcompliance: weak MAC allowed in SSH configuration"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires sshd effective configuration")
@pytest.mark.root(reason="required to inspect ssh cryptographic configuration")
def test_ssh_kex_are_strong(sshd: Sshd):
    """
    As per DISA STIG compliance requirement, the operating system must implement
    cryptographic mechanisms to prevent unauthorized disclosure of information
    and/or detect changes to information during transmission.
    This test verifies that SSH is configured with strong cryptographic algorithms
    and does not allow weak or insecure mechanisms.
    Ref: SRG-OS-000424-GPOS-00188
    """
    kex = sshd.get_config_section("kexalgorithms") or ""

    assert not re.search(
        r"diffie-hellman-group1-sha1", str(kex), re.IGNORECASE
    ), "stigcompliance: weak key exchange algorithm allowed in SSH configuration"
