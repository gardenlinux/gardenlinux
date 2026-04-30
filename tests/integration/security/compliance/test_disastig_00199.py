import pytest

"""
Ref: SRG-OS-000445-GPOS-00199

Verify the operating system verifies correct operation of all security
functions.
"""


@pytest.mark.feature("log")
@pytest.mark.booted("Needs working systemd")
def test_auditd_service_active(systemd):
    assert systemd.is_active("auditd")


@pytest.mark.feature("log")
@pytest.mark.booted("Needs working systemd")
def test_systemd_configured_to_restart_auditd_service(systemd):
    assert systemd.get_unit_properties("auditd")["Restart"] != "no"


@pytest.mark.feature("_selinux")
def test_selinux_enabled(lsm):
    assert "selinux" in lsm
