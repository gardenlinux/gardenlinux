import pytest
import os
from time import time
from datetime import datetime

from plugins.shell import ShellRunner
from plugins.timedatectl import TimeDateCtl, TimeSyncStatus
from plugins.timeconf import clocksource, chrony_config_file, ptp_hyperv_dev
from plugins.systemd import Systemd
from plugins.systemd_detect_virt import systemd_detect_virt, Hypervisor

@pytest.mark.booted(reason="NTP server configuration is read at runtime")
def test_clock(shell: ShellRunner):
    """ Test clock skew """
    local_seconds = int(time())
    output = shell(cmd="date '+%s'", capture_output=True)
    remote_seconds = int(output.stdout)

    assert (
        abs(local_seconds - remote_seconds) < 5
    ), f"clock skew should be less than 5 seconds. Local time is {local_seconds} and remote time is {remote_seconds}"

@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("aws")
@pytest.mark.parametrize("expected_ntp_server", ["169.254.169.123"])
def test_correct_ntp_on_aws(timedatectl: TimeDateCtl, expected_ntp_server: str):
    assert expected_ntp_server == timedatectl.get_ntpserver().ip, f"ntp server is invalid. Expected {expected_ntp_server}."

@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("gcp")
@pytest.mark.parametrize("expected_ntp_server", ["metadata.google.internal"])
def test_correct_ntp_on_gcp(timedatectl: TimeDateCtl, expected_ntp_server: str):
    assert expected_ntp_server == timedatectl.get_ntpserver().hostname, f"ntp server is invalid. Expected {expected_ntp_server}."

@pytest.mark.flaky(reruns=3, reruns_delay=10, only_rerun="AssertionError")
@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("not azure")
def test_ntp(timedatectl: TimeDateCtl):
    timesyncstatus: TimeSyncStatus = timedatectl.get_timesync_status()
    assert timesyncstatus.ntp, f"NTP not activated"
    assert timesyncstatus.ntp_synchronized, f"NTP not synchronized"

@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("azure")
def test_systemd_timesyncd_disabled(systemd: Systemd):
    assert systemd.is_active("systemd-timesyncd") == False, f"Chrony instead of systemd-timesyncd should be active on Azure."

@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("azure")
def test_chrony_on_azure(systemd: Systemd):
    """
    Test for chrony as active time sync service on Azure.
    See: https://learn.microsoft.com/en-us/azure/virtual-machines/linux/time-sync#chrony
    """
    assert systemd.is_active("chrony"), f"Chrony should be active on Azure."

@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("(not azure and not container) and x86_64")
def test_clocksource_x86_64(systemd_detect_virt: Hypervisor, clocksource: str):
    match systemd_detect_virt:
        case Hypervisor.xen | Hypervisor.qemu:
            expected_clocksource = "tsc"
        case Hypervisor.kvm | Hypervisor.amazon:
            expected_clocksource = "kvm-clock"
        case _:
            assert False, f"unknown hypervisor {systemd_detect_virt}"

    assert clocksource, expected_clocksource

@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("(not azure and not container) and (aarch64 or arm64)")
def test_clocksource_arm(systemd_detect_virt: Hypervisor, clocksource: str):
    match systemd_detect_virt:
        case Hypervisor.kvm | Hypervisor.qemu | Hypervisor.amazon:
            expected_clocksource = "arch_sys_counter"
        case _:
            assert False, f"unknown hypervisor {systemd_detect_virt}"

    assert clocksource, expected_clocksource    

@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("azure")
def test_chrony_azure(chrony_config_file: str, ptp_hyperv_dev: str):
    """
    Check Chrony configuration for expected content according to https://learn.microsoft.com/en-us/azure/virtual-machines/linux/time-sync
    """
    expected_config = f"refclock PHC {ptp_hyperv_dev} poll 3 dpoll -2 offset 0"
    with open(chrony_config_file, "r") as f:
        actual_config = f.read()
        assert actual_config.find(expected_config) != -1, f"chrony config for ptp expected but not found"

@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("azure")
def test_azure_ptp_symlink(ptp_hyperv_dev: str):
    assert os.path.islink(ptp_hyperv_dev), f"{ptp_hyperv_dev} should always be a symlink."

@pytest.mark.parametrize("dir", ["/bin","/etc/ssh"])
def test_files_not_in_future(dir: str):
    """
    Validate that all files in the image have a timestamp in the past.
    """
    now = datetime.now()
    for root, dirs, filenames in os.walk(dir):
        for filename in filenames:
            file = os.path.join(root, filename)
            modification = datetime.fromtimestamp(os.path.getmtime(file))
            assert modification <= now, f"timestamp of {file} is in the future {modification} (now={now})"
