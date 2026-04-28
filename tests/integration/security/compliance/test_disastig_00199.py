import pytest

"""
Ref: SRG-OS-000445-GPOS-00199

Verify the operating system verifies correct operation of all security
functions.
"""


@pytest.mark.booted("Needs working systemd")
def test_auditd_service_active(systemd, dpkg):
    if dpkg.package_is_installed("auditd"):
        assert systemd.is_active("auditd")


@pytest.mark.booted("Needs working systemd")
def test_systemd_configured_to_restart_auditd_service(systemd, dpkg):
    if dpkg.package_is_installed("auditd"):
        assert systemd.get_unit_properties("auditd")["Restart"] != "no"


@pytest.mark.feature("firewall")
@pytest.mark.booted("Needs working systemd")
def test_firewall_service_active(systemd):
    assert systemd.is_active("nftables")


@pytest.mark.feature("firewall")
@pytest.mark.booted("Needs working systemd")
def test_systemd_configured_to_restart_firewall_service(systemd):
    assert systemd.get_unit_properties("nftables")["Restart"] != "no"


@pytest.mark.feature("selinux")
def test_selinux_enabled(shell):
    result = shell("sestatus", capture_output=True)
    status = [
        line.split(":")[1].trim()
        for line in result.stdout.splitlines()
        if line.split(":")[0] == "SELinux status"
    ]
    assert status[0] == "enabled"
