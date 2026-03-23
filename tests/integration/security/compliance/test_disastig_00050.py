import pytest

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
@pytest.mark.booted(reason="requires booted system")
@pytest.mark.root(reason="requires audit operations")
@pytest.mark.skip(reason="no way of currently testing this")
def test_ports_protocols_and_services_restricted(shell, systemd):
    """
    As per DISA STIG compliance requirements, its needed to verify
    the operating system is configured to prohibit or restrict the
    use of functions, ports, protocols, and/or servicesto
    verify that only approved ports and services are active.
    Ref: SRG-OS-000096-GPOS-00050
    """
    result = shell("ss -tuln", capture_output=True)
    assert result.returncode == 0, "stigcompliance: failed to list listening ports"

    open_ports = set()
    for line in result.stdout.splitlines():
        if "LISTEN" in line:
            port = line.split()[4].split(":")[-1]
            if port.isdigit():
                open_ports.add(int(port))
    return open_ports


@pytest.mark.feature("not container and not gardener")
@pytest.mark.booted(reason="requires booted system")
@pytest.mark.root(reason="requires audit operations")
def test_only_ssh_open_port_is_allowed(open_ports):
    unauthorized_ports = open_ports - {22}

    assert (
        not unauthorized_ports
    ), f"stigcompliance: unauthorized ports open: {unauthorized_ports}"


@pytest.mark.feature("not container and gardener")
@pytest.mark.booted(reason="requires booted system")
@pytest.mark.root(reason="requires audit operations")
def test_only_a_subset_of_open_ports_is_allowed(open_ports):
    unauthorized_ports = open_ports - {
        22,
        53,
        111,
        3260,
    }  # ssh, dns, portmapper, iscsi-target

    assert (
        not unauthorized_ports
    ), f"stigcompliance: unauthorized ports open: {unauthorized_ports}"


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="requires booted system")
@pytest.mark.root(reason="requires audit operations")
def test_dangerous_services_are_not_running(systemd):
    running_services = {unit.unit for unit in systemd.list_running_units()}

    found_dangerous = [svc for svc in FORBIDDEN_SERVICES if svc in running_services]

    assert (
        not found_dangerous
    ), f"stigcompliance: dangerous services running: {found_dangerous}"
