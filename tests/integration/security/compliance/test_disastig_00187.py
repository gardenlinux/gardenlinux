import pytest
from plugins.systemd import Systemd


@pytest.mark.booted(reason="requires booted system to verify services")
@pytest.mark.root(reason="required to inspect system services")
def test_telnet_service_disabled(systemd: Systemd):
    """
    As per DISA STIG compliance requirement, the operating system must protect
    the confidentiality and integrity of transmitted information.
    This test verifies that insecure network services (which transmit data
    without encryption) are not enabled on the system.
    Ref: SRG-OS-000423-GPOS-00187
    """
    assert not systemd.is_enabled(
        "telnet.service"
    ), "stigcompliance: insecure service telnet.service is enabled"


@pytest.mark.booted(reason="requires booted system to verify services")
@pytest.mark.root(reason="required to inspect system services")
def test_telnet_service_active(systemd: Systemd):
    """
    As per DISA STIG compliance requirement, the operating system must protect
    the confidentiality and integrity of transmitted information.
    This test verifies that insecure network services (which transmit data
    without encryption) are not enabled on the system.
    Ref: SRG-OS-000423-GPOS-00187
    """

    assert not systemd.is_active(
        "telnet.service"
    ), "stigcompliance: insecure service telnet.service is active"


@pytest.mark.booted(reason="requires booted system to verify services")
@pytest.mark.root(reason="required to inspect system services")
def test_rsh_service_disabled(systemd: Systemd):
    """
    As per DISA STIG compliance requirement, the operating system must protect
    the confidentiality and integrity of transmitted information.
    This test verifies that insecure network services (which transmit data
    without encryption) are not enabled on the system.
    Ref: SRG-OS-000423-GPOS-00187
    """
    assert not systemd.is_enabled(
        "rsh.service"
    ), "stigcompliance: insecure service rsh.service is enabled"


@pytest.mark.booted(reason="requires booted system to verify services")
@pytest.mark.root(reason="required to inspect system services")
def test_rsh_service_active(systemd: Systemd):
    """
    As per DISA STIG compliance requirement, the operating system must protect
    the confidentiality and integrity of transmitted information.
    This test verifies that insecure network services (which transmit data
    without encryption) are not enabled on the system.
    Ref: SRG-OS-000423-GPOS-00187
    """
    assert not systemd.is_active(
        "rsh.service"
    ), "stigcompliance: insecure service rsh.service is active"


@pytest.mark.booted(reason="requires booted system to verify services")
@pytest.mark.root(reason="required to inspect system services")
def test_rexec_service_disabled(systemd: Systemd):
    """
    As per DISA STIG compliance requirement, the operating system must protect
    the confidentiality and integrity of transmitted information.
    This test verifies that insecure network services (which transmit data
    without encryption) are not enabled on the system.
    Ref: SRG-OS-000423-GPOS-00187
    """
    assert not systemd.is_enabled(
        "rexec.service"
    ), "stigcompliance: insecure service rexec.service is enabled"


@pytest.mark.booted(reason="requires booted system to verify services")
@pytest.mark.root(reason="required to inspect system services")
def test_rexec_service_active(systemd: Systemd):
    """
    As per DISA STIG compliance requirement, the operating system must protect
    the confidentiality and integrity of transmitted information.
    This test verifies that insecure network services (which transmit data
    without encryption) are not enabled on the system.
    Ref: SRG-OS-000423-GPOS-00187
    """
    assert not systemd.is_active(
        "rexec.service"
    ), "stigcompliance: insecure service rexec.service is active"


@pytest.mark.booted(reason="requires booted system to verify services")
@pytest.mark.root(reason="required to inspect system services")
def test_rlogin_service_disabled(systemd: Systemd):
    """
    As per DISA STIG compliance requirement, the operating system must protect
    the confidentiality and integrity of transmitted information.
    This test verifies that insecure network services (which transmit data
    without encryption) are not enabled on the system.
    Ref: SRG-OS-000423-GPOS-00187
    """
    assert not systemd.is_enabled(
        "rlogin.service"
    ), "stigcompliance: insecure service rlogin.service is enabled"


@pytest.mark.booted(reason="requires booted system to verify services")
@pytest.mark.root(reason="required to inspect system services")
def test_rlogin_service_active(systemd: Systemd):
    """
    As per DISA STIG compliance requirement, the operating system must protect
    the confidentiality and integrity of transmitted information.
    This test verifies that insecure network services (which transmit data
    without encryption) are not enabled on the system.
    Ref: SRG-OS-000423-GPOS-00187
    """
    assert not systemd.is_active(
        "rlogin.service"
    ), "stigcompliance: insecure service rlogin.service is active"


@pytest.mark.booted(reason="requires booted system to verify services")
@pytest.mark.root(reason="required to inspect system services")
def test_vsftpd_service_disabled(systemd: Systemd):
    """
    As per DISA STIG compliance requirement, the operating system must protect
    the confidentiality and integrity of transmitted information.
    This test verifies that insecure network services (which transmit data
    without encryption) are not enabled on the system.
    Ref: SRG-OS-000423-GPOS-00187
    """
    assert not systemd.is_enabled(
        "vsftpd.service"
    ), "stigcompliance: insecure service vsftpd.service is enabled"


@pytest.mark.booted(reason="requires booted system to verify services")
@pytest.mark.root(reason="required to inspect system services")
def test_vsftpd_service_active(systemd: Systemd):
    """
    As per DISA STIG compliance requirement, the operating system must protect
    the confidentiality and integrity of transmitted information.
    This test verifies that insecure network services (which transmit data
    without encryption) are not enabled on the system.
    Ref: SRG-OS-000423-GPOS-00187
    """
    assert not systemd.is_active(
        "vsftpd.service"
    ), "stigcompliance: insecure service vsftpd.service is active"
