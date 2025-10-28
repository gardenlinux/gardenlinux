import pytest


@pytest.mark.feature("aide")
@pytest.mark.root(reason="Required to read root's crontab")
@pytest.mark.booted(reason="cron is expected to be configured at runtime")
def test_aide_cron_is_configured(shell):
    """
    Ensure that a scheduled cron job exists to run AIDE integrity checks.
    This is a CIS requirement: AIDE must run automatically.
    """
    result = shell(
        "cat /var/spool/cron/crontabs/root",
        capture_output=True,
        ignore_exit_code=True,
    )

    expected = "/usr/bin/aide --check --config /etc/aide/aide.conf"

    assert (
        result.returncode == 0
    ), f"""
No root crontab found — AIDE is not scheduled (missing CIS requirement).
Expected cron entry:
  {expected}
Make sure aide-init.service creates /var/spool/cron/crontabs/root.
"""

    assert (
        expected in result.stdout
    ), f"""
AIDE cron job missing — automatic integrity checks are NOT scheduled.
Expected to find line containing:
  {expected}
Full cron content:
{result.stdout}
"""
