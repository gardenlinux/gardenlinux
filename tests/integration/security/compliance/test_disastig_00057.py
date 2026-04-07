import pytest


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="requires sshd effective configuration")
@pytest.mark.root(reason="required to inspect ssh configuration")
def test_ssh_available_for_network_access(sshd):
    """
    As per DISA STIG compliance requirement, the operating system must implement
    replay-resistant authentication mechanisms for network access to privileged accounts.
    This test verifies that SSH (a replay-resistant authentication mechanism)
    is available for network access.
    Ref: SRG-OS-000112-GPOS-00057
    """

    config = sshd.get_config()

    assert config, "stigcompliance: sshd configuration not available"
