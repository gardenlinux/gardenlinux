import pytest
from plugins.sshd import Sshd

"""
Ref: SRG-OS-000112-GPOS-00057

Verify the operating system implements replay-resistant authentication
mechanisms for network access to privileged accounts.
"""


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-ssh-sshd-config-d-disaSTIG"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="SSH KexAlgorithms are hardened by disaSTIGmedium"
)
@pytest.mark.booted(reason="requires sshd effective configuration")
@pytest.mark.root(reason="required to inspect SSH configuration")
def test_ssh_kex_algorithms_are_strong(sshd: Sshd) -> None:
    approved = {
        "diffie-hellman-group14-sha256",
        "diffie-hellman-group16-sha512",
        "diffie-hellman-group18-sha512",
        "ecdh-sha2-nistp384",
        "ecdh-sha2-nistp521",
    }
    kex = sshd.get_config_section("kexalgorithms")
    if isinstance(kex, str):
        kex_list = [k.strip() for k in kex.split(",")]
    else:
        kex_list = [k.strip() for k in ",".join(kex).split(",")]
    assert all(
        k in approved for k in kex_list
    ), f"stigcompliance: SSH KexAlgorithms contain non-approved algorithms: {kex_list}"
