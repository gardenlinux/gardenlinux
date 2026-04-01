import pytest
from plugins.dpkg import Dpkg


@pytest.mark.feature(
    "not container and not lima and not gardener and not capi and not baremetal"
)
@pytest.mark.booted(reason="requires SSH runtime configuration")
@pytest.mark.root(reason="requires access to SSH configuration")
def test_ssh_strong_macs_present(sshd, dpkg: Dpkg):
    """
    As per DISA STIG compliance requirements, the operating system must implement
    cryptographic mechanisms to protect the integrity of nonlocal maintenance and
    diagnostic communications, when used for nonlocal maintenance sessions.
    This test verifies that SSH is configured with strong MAC algorithms to ensure
    integrity protection for remote sessions.
    Ref: SRG-OS-000393-GPOS-00173
    """

    if not dpkg.package_is_installed("openssh-server"):
        pytest.skip(
            "openssh-server not installed; no nonlocal maintenance mechanism present"
        )

    config = sshd.get_config()
    macs = config.get("macs")

    assert macs is not None, "stigcompliance: SSH MACs configuration not defined"

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
        "hmac-sha2-256-etm@openssh.com",
        "hmac-sha2-512-etm@openssh.com",
    }

    assert any(
        mac in strong_macs for mac in mac_list
    ), "stigcompliance: no strong MAC algorithms configured for SSH integrity protection"


@pytest.mark.feature(
    "not container and not lima and not gardener and not capi and not baremetal"
)
@pytest.mark.booted(reason="requires SSH runtime configuration")
@pytest.mark.root(reason="requires access to SSH configuration")
def test_ssh_weak_macs_not_present(sshd, dpkg: Dpkg):
    """
    As per DISA STIG compliance requirements, the operating system must implement
    cryptographic mechanisms to protect the integrity of nonlocal maintenance and
    diagnostic communications, when used for nonlocal maintenance sessions.
    This test verifies that SSH is not configured with weak MAC algorithms that
    would undermine integrity protection.
    Ref: SRG-OS-000393-GPOS-00173
    """

    if not dpkg.package_is_installed("openssh-server"):
        pytest.skip(
            "openssh-server not installed; no nonlocal maintenance mechanism present"
        )

    config = sshd.get_config()
    macs = config.get("macs")

    assert macs is not None, "stigcompliance: SSH MACs configuration not defined"

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
