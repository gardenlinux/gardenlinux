import pytest
from plugins.systemd import Systemd

INSECURE_SERVICES = [
    "telnet.service",
    "rsh.service",
    "rexec.service",
    "rlogin.service",
    "vsftpd.service",
]


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires booted system to verify services")
@pytest.mark.root(reason="required to inspect system services")
def test_insecure_network_services_disabled(systemd: Systemd):
    """
    As per DISA STIG compliance requirement, the operating system must protect
    the confidentiality and integrity of transmitted information.
    This test verifies that insecure network services (which transmit data
    without encryption) are not enabled on the system.
    Ref: SRG-OS-000423-GPOS-00187
    """

    for service in INSECURE_SERVICES:
        assert not systemd.is_enabled(
            service
        ), f"stigcompliance: insecure service {service} is enabled"

        assert not systemd.is_active(
            service
        ), f"stigcompliance: insecure service {service} is active"
