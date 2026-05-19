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


@pytest.mark.testcov(["GL-TESTCOV-aide-service-aide-init-enable"])
@pytest.mark.feature("aide", reason="aide-init.service is enabled by the aide feature")
@pytest.mark.booted(reason="requires systemd to query unit enable state")
def test_aide_init_service_is_enabled(systemd) -> None:
    assert systemd.is_enabled(
        "aide-init.service"
    ), "stigcompliance: aide-init.service is not enabled"


@pytest.mark.testcov(["GL-TESTCOV-aide-service-aide-check-timer-enable"])
@pytest.mark.feature("aide", reason="aide-check.timer is enabled by the aide feature")
@pytest.mark.booted(reason="requires systemd to query unit enable state")
def test_aide_check_timer_is_enabled(systemd) -> None:
    assert systemd.is_enabled(
        "aide-check.timer"
    ), "stigcompliance: aide-check.timer is not enabled"
