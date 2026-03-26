import pytest

ALLOWED_PORTS = {22, 53, 2601, 111, 2616, 3260, 2623, 39397}

FORBIDDEN_SERVICES = [
    "telnet.service",
    "vsftpd.service",
    "rsh.service",
    "avahi-daemon.service",
    "cups.service",
]


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires booted system")
@pytest.mark.root(reason="requires audit operations")
@pytest.mark.modify(reason="required for DISA STIG check")
def test_ports_protocols_and_services_restricted(shell):
    """
    As per DISA STIG compliance requirements, it is needed to verify
    that only approved ports and services are active.
    Ref: SRG-OS-000096-GPOS-00050
    """

    # --- Check open ports ---
    result = shell("ss -tuln", capture_output=True)
    assert result.returncode == 0, "stigcompliance: failed to list listening ports"

    open_ports = set()
    for line in result.stdout.splitlines():
        if "LISTEN" in line:
            parts = line.split()
            if len(parts) >= 5:
                address = parts[4]
                port = address.split(":")[-1]
                if port.isdigit():
                    open_ports.add(int(port))

    unauthorized_ports = open_ports - ALLOWED_PORTS

    assert (
        not unauthorized_ports
    ), f"stigcompliance: unauthorized ports open: {unauthorized_ports}"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires booted system")
@pytest.mark.root(reason="requires audit operations")
@pytest.mark.modify(reason="required for DISA STIG check")
def test_forbidden_services_not_running(shell):
    """
    As per DISA STIG compliance requirements, it is needed to verify
    that only approved ports and services are active.
    Ref: SRG-OS-000096-GPOS-00050
    """

    result = shell(
        "systemctl list-units --type=service --state=running --no-legend",
        capture_output=True,
    )
    assert result.returncode == 0, "stigcompliance: failed to list running services"

    running_services = {line.split()[0] for line in result.stdout.splitlines() if line}

    found_forbidden = [svc for svc in FORBIDDEN_SERVICES if svc in running_services]

    assert (
        not found_forbidden
    ), f"stigcompliance: forbidden services running: {found_forbidden}"
