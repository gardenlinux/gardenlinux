import pytest
from plugins.sshd import Sshd
from plugins.systemd import Systemd


@pytest.mark.booted(reason="requires sshd effective configuration")
@pytest.mark.root(reason="required to inspect ssh configuration")
def test_sshd_config_present(sshd: Sshd):
    """
    As per DISA STIG compliance requirement, the operating system must implement
    replay-resistant authentication mechanisms for network access to privileged accounts.
    This test verifies that SSH configuration is available.
    Ref: SRG-OS-000112-GPOS-00057
    """
    kexpresence = sshd.get_config_section("kexalgorithms")
    assert kexpresence is not None, "stigcompliance: sshd configuration not available"


@pytest.mark.booted(reason="requires systemd service state")
@pytest.mark.root(reason="required to inspect ssh service")
def test_sshd_service_active(systemd: Systemd):
    """
    As per DISA STIG compliance requirement, the operating system must implement
    replay-resistant authentication mechanisms for network access to privileged accounts.
    This test verifies that sshd service is active.
    Ref: SRG-OS-000112-GPOS-00057
    """
    assert systemd.is_active(
        "sshd.service"
    ), "stigcompliance: sshd.service is not active"
