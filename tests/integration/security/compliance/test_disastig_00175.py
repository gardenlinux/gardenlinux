import pytest
from plugins.dpkg import Dpkg


@pytest.mark.feature(
    "not container and not lima and not gardener and not capi and not baremetal"
)
@pytest.mark.booted(reason="requires SSH runtime configuration")
@pytest.mark.root(reason="requires access to SSH configuration")
def test_ssh_client_alive_interval_configured(sshd, dpkg: Dpkg):
    """
    As per DISA STIG compliance requirements, the operating system must verify
    remote disconnection at the termination of nonlocal maintenance and diagnostic
    sessions, when used for nonlocal maintenance sessions.
    This test verifies that SSH is configured with ClientAliveInterval to detect
    inactive or disconnected sessions.
    Ref: SRG-OS-000395-GPOS-00175
    """

    if not dpkg.package_is_installed("openssh-server"):
        pytest.skip(
            "openssh-server not installed; no nonlocal maintenance mechanism present"
        )

    config = sshd.get_config()

    interval = config.get("clientaliveinterval")

    assert interval is not None, "stigcompliance: ClientAliveInterval not configured"

    assert (
        interval != "0"
    ), "stigcompliance: ClientAliveInterval is disabled (0), session timeout not enforced"
