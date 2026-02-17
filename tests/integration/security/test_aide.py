import pytest
from plugins.file import File
from plugins.parse_file import ParseFile
from plugins.systemd import Systemd


@pytest.mark.setting_ids(["GL-SET-aide-script-aide-init-onboot"])
@pytest.mark.feature("aide")
def test_aide_init_onboot_script_exists(file: File):
    """Test that AIDE initialization script exists"""
    assert file.is_regular_file("/usr/local/sbin/aide-init-onboot.sh")


@pytest.mark.setting_ids(["GL-SET-aide-service-aide-check-unit"])
@pytest.mark.feature("aide")
def test_aide_check_unit_exists(file):
    """Test that aide-check.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/aide-check.service")


@pytest.mark.setting_ids(["GL-SET-aide-service-aide-init-unit"])
@pytest.mark.feature("aide")
def test_aide_init_unit_exists(file):
    """Test that aide-init.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/aide-init.service")


@pytest.mark.setting_ids(["GL-SET-aide-service-aide-init-enable"])
@pytest.mark.feature("aide")
@pytest.mark.booted(reason="Requires systemd")
def test_aide_aide_init_service_enabled(systemd: Systemd):
    """Test that aide-init.service is enabled"""
    assert systemd.is_enabled("aide-init.service")


@pytest.mark.setting_ids(["GL-SET-aide-service-aide-init-enable"])
@pytest.mark.feature("aide")
@pytest.mark.booted(reason="Requires systemd")
def test_aide_aide_init_service_active(systemd: Systemd):
    """Test that aide-init.service is active"""
    assert systemd.is_active("aide-init.service")


@pytest.mark.setting_ids(["GL-SET-aide-service-aide-check-timer-enable"])
@pytest.mark.feature("aide")
@pytest.mark.booted(reason="Requires systemd")
def test_aide_timer_aide_check_service_enabled(systemd: Systemd):
    """Test that aide-check.timer is enabled"""
    assert systemd.is_enabled("aide-check.timer")


@pytest.mark.setting_ids(["GL-SET-aide-service-aide-check-timer-enable"])
@pytest.mark.feature("aide")
@pytest.mark.booted(reason="Requires systemd")
def test_aide_timer_aide_check_service_active(systemd: Systemd):
    """Test that aide-check.timer is active"""
    assert systemd.is_active("aide-check.timer")


@pytest.mark.setting_ids(["GL-SET-aide-service-aide-check-timer"])
@pytest.mark.feature("aide")
@pytest.mark.root(reason="Required to query systemd units")
@pytest.mark.booted(reason="systemd timers are expected to be configured at runtime")
def test_aide_timer_exists(systemd: Systemd):
    """Verify that the AIDE timer unit exists."""
    timer = "aide-check.timer"
    units = systemd.list_units()
    matches = [u for u in units if u.unit == timer]
    assert matches, f"AIDE timer '{timer}' not found — CIS requirement failed"


@pytest.mark.setting_ids(["GL-SET-aide-service-aide-check-timer"])
@pytest.mark.feature("aide")
@pytest.mark.root(reason="Required to query systemd units")
@pytest.mark.booted(reason="systemd timers are expected to be configured at runtime")
def test_aide_timer_loaded(systemd: Systemd):
    """Verify that the AIDE timer unit is loaded."""
    timer = "aide-check.timer"
    units = systemd.list_units()
    matches = [u for u in units if u.unit == timer]
    assert (
        matches[0].load == "loaded"
    ), f"AIDE timer must be loaded but is {matches[0].load}"


@pytest.mark.setting_ids(["GL-SET-aide-service-aide-check-timer"])
@pytest.mark.feature("aide")
@pytest.mark.root(reason="Required to query systemd units")
@pytest.mark.booted(reason="systemd timers are expected to be configured at runtime")
def test_aide_timer_active(systemd: Systemd):
    """Verify that the AIDE timer unit is active."""
    timer = "aide-check.timer"
    assert systemd.is_active(timer), f"AIDE timer '{timer}' exists but is not active."


@pytest.mark.setting_ids(["GL-SET-aide-service-aide-check-timer"])
@pytest.mark.feature("aide")
@pytest.mark.root(reason="Required to query systemd units")
@pytest.mark.booted(reason="systemd timers are expected to be configured at runtime")
def test_aide_timer_state(systemd: Systemd):
    """Verify that the AIDE timer is in 'waiting' or 'running' state."""
    timer = "aide-check.timer"
    units = systemd.list_units()
    matches = [u for u in units if u.unit == timer]
    unit = matches[0]
    assert unit.sub in (
        "waiting",
        "running",
    ), f"AIDE timer scheduling state unexpected (sub={unit.sub})"


@pytest.mark.feature("aide")
@pytest.mark.root(reason="Required to read AIDE configuration")
@pytest.mark.booted(reason="AIDE configuration must exist at runtime")
def test_aide_conf_contains_faillog_entry(parse_file: ParseFile):
    """Ensure that AIDE configuration exists and includes '/var/log/faillog Full'"""
    conf_path = "/etc/aide/aide.conf"
    lines = parse_file.lines(conf_path)
    expected_line = "/var/log/faillog Full"
    assert (
        expected_line in lines
    ), f"Expected '{expected_line}' not found in {conf_path}. "
