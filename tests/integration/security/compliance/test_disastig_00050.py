import pytest

"""
Ref: SRG-OS-000096-GPOS-00050

Verify the operating system is configured to prohibit or restrict the use of
functions, ports, protocols, and/or services, as defined in the PPSM CAL and
vulnerability assessments.
"""

ALLOWED_PORTS = {22, 53}

FORBIDDEN_SERVICES = [
    "telnet.service",
    "vsftpd.service",
    "rsh.service",
    "avahi-daemon.service",
    "cups.service",
]


@pytest.mark.feature(
    "not container and not gardener and not lima and not capi and not baremetal"
)
@pytest.mark.security_id(203638)
@pytest.mark.booted(reason="requires booted system")
@pytest.mark.root(reason="requires audit operations")
@pytest.mark.skip(reason="no way of currently testing this")
def test_ports_protocols_and_services_restricted(shell, systemd):
    result = shell("ss -tuln", capture_output=True)
    assert result.returncode == 0, "stigcompliance: failed to list listening ports"

    open_ports = set()
    for line in result.stdout.splitlines():
        if "LISTEN" in line:
            port = line.split()[4].split(":")[-1]
            if port.isdigit():
                open_ports.add(int(port))

    unauthorized_ports = open_ports - ALLOWED_PORTS

    assert (
        not unauthorized_ports
    ), f"stigcompliance: unauthorized ports open: {unauthorized_ports}"

    running_units = systemd.list_running_units()

    running_names = {unit.unit for unit in running_units}

    found_forbidden = [svc for svc in FORBIDDEN_SERVICES if svc in running_names]

    assert (
        not found_forbidden
    ), f"stigcompliance: forbidden services running: {found_forbidden}"
