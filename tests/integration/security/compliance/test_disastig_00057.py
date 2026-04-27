import pytest


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="requires sshd effective configuration")
@pytest.mark.root(reason="required to inspect ssh configuration")
def test_sshd_client_alive_interval_configured(sshd):
    """
    As per DISA STIG compliance requirement, the operating system must use SSH
    to protect the confidentiality and integrity of transmitted information.
    This test verifies that ClientAliveInterval is configured to a non-zero
    value not exceeding 900 seconds, ensuring inactive sessions are terminated.
    Ref: SRG-OS-000112-GPOS-00057 (V-238213)
    """
    interval = sshd.get_config_section("clientaliveinterval")
    assert (
        interval is not None and interval != "0" and int(interval) <= 900
    ), f"stigcompliance: ClientAliveInterval must be set between 1 and 900, got: {interval}"


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="requires systemd service state")
@pytest.mark.root(reason="required to inspect ssh service")
def test_sshd_service_active(systemd):
    """
    As per DISA STIG compliance requirement, the operating system must use SSH
    to protect the confidentiality and integrity of transmitted information.
    This test verifies that sshd.service is active, ensuring SSH is available
    to protect transmitted information.
    Ref: SRG-OS-000112-GPOS-00057
    """
    assert systemd.is_active(
        "sshd.service"
    ), "stigcompliance: sshd.service is not active"
