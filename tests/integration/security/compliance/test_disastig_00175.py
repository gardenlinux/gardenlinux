import pytest

"""
Ref: SRG-OS-000395-GPOS-00175

Verify the operating system verifies remote disconnection at the termination of
nonlocal maintenance and diagnostic sessions, when used for nonlocal
maintenance sessions.
"""


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="requires SSH runtime configuration")
@pytest.mark.root(reason="requires access to SSH configuration")
def test_ssh_client_alive_interval_configured(sshd):
    interval = sshd.get_config_section("clientaliveinterval")

    assert (
        interval != "0"
    ), "stigcompliance: ClientAliveInterval is disabled (0), session timeout not enforced"
