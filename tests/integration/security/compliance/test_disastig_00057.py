"""
Ref: SRG-OS-000112-GPOS-00057

Verify the operating system implements replay-resistant authentication
mechanisms for network access to privileged accounts.
"""

import re

import pytest
from plugins.sshd import Sshd


@pytest.mark.security_id(203645)
@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-ssh-sshd-config-d-disaSTIG"])
@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="requires sshd effective configuration")
@pytest.mark.root(reason="required to inspect SSH configuration")
def test_ssh_kex_algorithms_are_replay_resistant(sshd: Sshd) -> None:
    """Verify SSH KexAlgorithms exclude non-replay-resistant algorithms (diffie-hellman-group1-sha1, diffie-hellman-group14-sha1)."""
    kex = sshd.get_config_section("kexalgorithms") or ""

    assert not re.search(
        r"diffie-hellman-group1-sha1|diffie-hellman-group14-sha1",
        str(kex),
        re.IGNORECASE,
    ), "stigcompliance: SSH KexAlgorithms contain non-replay-resistant algorithms"


@pytest.mark.security_id(203645)
@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-ssh-sshd-config-d-disaSTIG"])
@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="requires sshd effective configuration")
@pytest.mark.root(reason="required to inspect SSH configuration")
def test_ssh_kex_includes_ecdh(sshd: Sshd) -> None:
    """Verify SSH KexAlgorithms include an approved ECDH algorithm (ecdh-sha2-nistp384 or ecdh-sha2-nistp521)."""
    kex = sshd.get_config_section("kexalgorithms") or ""

    assert re.search(
        r"ecdh-sha2-nistp(384|521)", str(kex), re.IGNORECASE
    ), "stigcompliance: no approved ECDH KexAlgorithm configured"
