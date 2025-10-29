import pytest

@pytest.mark.feature("aide")
@pytest.mark.root(reason="Required to query systemd units")
@pytest.mark.booted(reason="systemd timers are expected to be configured at runtime")
def test_aide_timer_is_configured(shell):
    """
    Ensure that a systemd timer exists to run AIDE integrity checks.
    This is a CIS requirement: AIDE must run automatically.
    """
    # Check if the timer exists and is enabled
    result = shell(
        "systemctl is-enabled aide-check.timer",
        capture_output=True,
        ignore_exit_code=True,
    )

    assert (
        result.returncode == 0 and "enabled" in result.stdout
    ), f"""
AIDE systemd timer is NOT enabled — automatic integrity checks are NOT scheduled.
Expected: aide-check.timer to be enabled.
Output:
{result.stdout or result.stderr}
"""

    # Check next scheduled runtime — ensures it's actually loaded and active
    result = shell(
        "systemctl status aide-check.timer",
        capture_output=True,
        ignore_exit_code=True,
    )

    assert (
        "Active: active" in result.stdout
        and ("10:" in result.stdout or "OnCalendar=" in result.stdout)
    ), f"""
AIDE systemd timer is present but seems inactive or misconfigured.
Expected: active with correct schedule around 10:00 daily.
Full status:
{result.stdout}
"""

