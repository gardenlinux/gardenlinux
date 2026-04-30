import pytest

"""
Ref: SRG-OS-000355-GPOS-00143

Verify the operating system, for networked systems, compares internal
information system clocks at least every 24 hours with an authoritative time
source.

Ref: SRG-OS-000356-GPOS-00144

Verify the operating system synchronizes internal information system clocks to
the authoritative time source when the time difference is greater than one
second.

"""


@pytest.mark.hypervisor(
    "gdch or microsoft", reason="Need PTP timesync sources to be reachable"
)
@pytest.mark.booted(reason="requires running systemd")
def test_time_sync_ptp_daemon_running(systemd):
    assert systemd.is_active("chrony")


@pytest.mark.hypervisor("not (azure or gdch)")
@pytest.mark.booted(reason="requires running systemd")
def test_time_sync_ntp_daemon_running(systemd):
    assert systemd.is_active("systemd-timesyncd")


@pytest.mark.hypervisor(
    "azure or gdch or google or microsoft",
    reason="Need NTP/PTP timesync sources to be reachable",
)
@pytest.mark.booted(reason="requires running systemd")
def test_time_is_actively_synced(timedatectl, shell):
    assert timedatectl.get_timesync_status().ntp_synchronized


@pytest.mark.booted(reason="requires running systemd")
def test_time_is_synced_at_least_once_a_day(timedatectl):
    assert timedatectl.get_timesync_status().poll_interval_max < (24 * 60 * 60)
