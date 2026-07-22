"""
Ref: SRG-OS-000393-GPOS-00173

Verify the operating system implements cryptographic mechanisms to protect the
integrity of nonlocal maintenance and diagnostic communications, when used for
nonlocal maintenance sessions.
"""

import pytest
from plugins.dpkg import Dpkg


@pytest.mark.security_id(203736)
@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-ssh-sshd-config-d-disaSTIG"])
@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="requires SSH runtime configuration")
@pytest.mark.root(reason="requires access to SSH configuration")
def test_ssh_strong_macs_present(sshd, dpkg: Dpkg):
    """Verify sshd MACs are limited to strong algorithms (SHA2)."""
    macs = sshd.get_config_section("macs")

    if isinstance(macs, str):
        macs = [macs]
    elif isinstance(macs, set):
        macs = list(macs)

    mac_list = []
    for entry in macs:
        mac_list.extend([m.strip() for m in entry.split(",")])

    strong_macs = {
        "hmac-sha2-256",
        "hmac-sha2-512",
    }

    assert all(
        mac in strong_macs for mac in mac_list
    ), "stigcompliance: no strong MAC algorithms configured for SSH integrity protection"


@pytest.mark.security_id(203736)
@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-ssh-sshd-config-d-disaSTIG"])
@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="requires SSH runtime configuration")
@pytest.mark.root(reason="requires access to SSH configuration")
def test_ssh_weak_macs_not_present(sshd):
    """Verify sshd does not advertise weak MAC algorithms (hmac-md5)."""
    macs = sshd.get_config_section("macs")

    if isinstance(macs, str):
        macs = [macs]
    elif isinstance(macs, set):
        macs = list(macs)

    mac_list = []
    for entry in macs:
        mac_list.extend([m.strip() for m in entry.split(",")])

    weak_macs = {
        "hmac-md5",
        "hmac-md5-96",
    }

    assert not any(
        mac in weak_macs for mac in mac_list
    ), "stigcompliance: weak MAC algorithms present in SSH configuration"
