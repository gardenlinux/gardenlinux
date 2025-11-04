import pytest
from plugins.systemd import Systemd

@pytest.mark.feature("aide")
@pytest.mark.root(reason="Required to query systemd units")
@pytest.mark.booted(reason="systemd timers are expected to be configured at runtime")
def test_aide_timer_is_configured(systemd: Systemd):
    """
    Ensure that a systemd timer exists to run AIDE integrity checks.
    This is a CIS requirement: AIDE must run automatically.
    """

    timer = "aide-check.timer"

    # To check if the aide timer unit exists and is loaded well
    units = systemd.list_units()
    matches = [u for u in units if u.unit == timer]

    assert matches, (
        f"AIDE timer '{timer}' not found — CIS requirement failed"
    )

    unit = matches[0]
    assert unit.load == "loaded", (
        f"AIDE timer must be loaded but is {unit.load}"
    )

    # aide timer should be active in systemd
    assert systemd.is_active(timer), (
        f"AIDE timer exists but is not active (active={unit.active}, sub={unit.sub})"
    )

    # aide timer in waiting / running
    assert unit.sub in ("waiting", "running"), (
        f"AIDE timer scheduling state unexpected (sub={unit.sub})"
    )
