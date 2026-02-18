from pathlib import Path

import pytest
from plugins.parse_file import ParseFile
from plugins.systemd import Systemd


@pytest.mark.feature("aide")
@pytest.mark.root(reason="Required to query systemd units")
@pytest.mark.booted(reason="systemd timers are expected to be configured at runtime")
def test_aide_timer_exists(systemd: Systemd):
    """Verify that the AIDE timer unit exists."""
    timer = "aide-check.timer"
    units = systemd.list_units()
    matches = [u for u in units if u.unit == timer]
    assert matches, f"AIDE timer '{timer}' not found — CIS requirement failed"


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


@pytest.mark.feature("aide")
@pytest.mark.root(reason="Required to query systemd units")
@pytest.mark.booted(reason="systemd timers are expected to be configured at runtime")
def test_aide_timer_active(systemd: Systemd):
    """Verify that the AIDE timer unit is active."""
    timer = "aide-check.timer"
    assert systemd.is_active(timer), f"AIDE timer '{timer}' exists but is not active."


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
