import os
from datetime import datetime
from time import time

import pytest
from plugins.shell import ShellRunner
from plugins.systemd import Systemd
from plugins.systemd_detect_virt import Hypervisor, systemd_detect_virt
from plugins.timeconf import chrony_config_file, clocksource, ptp_hyperv_dev
from plugins.timedatectl import TimeDateCtl, TimeSyncStatus


@pytest.mark.booted(reason="NTP server configuration is read at runtime")
def test_clock(shell: ShellRunner):
    """Test clock skew"""
    local_seconds = int(time())
    output = shell(cmd="date '+%s'", capture_output=True)
    remote_seconds = int(output.stdout)

    assert (
        abs(local_seconds - remote_seconds) < 5
    ), f"clock skew should be less than 5 seconds. Local time is {local_seconds} and remote time is {remote_seconds}"


@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("aws")
@pytest.mark.hypervisor("amazon")
def test_correct_ntp_on_aws(timedatectl: TimeDateCtl):
    ntp_ip = timedatectl.get_ntpserver().ip
    assert (
        ntp_ip == "169.254.169.123"
    ), f"ntp server is invalid. Expected '169.254.169.123' got '{ntp_ip}'."


@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("gcp")
@pytest.mark.hypervisor("google")
def test_correct_ntp_on_gcp(timedatectl: TimeDateCtl):
    ntp_hostname = timedatectl.get_ntpserver().hostname
    assert (
        ntp_hostname == "metadata.google.internal"
    ), f"ntp server is invalid. Expected 'metadata.google.internal' got '{ntp_hostname}'."


@pytest.mark.flaky(reruns=10, reruns_delay=30, only_rerun="AssertionError")
@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("not azure and not aws and not gcp and not gdch")
def test_ntp(timedatectl: TimeDateCtl):
    """
    Validate that systemd-timesyncd is installed and active.
    """
    # Verify image configuration
    assert (
        timedatectl.has_timesync_installed()
    ), "systemd-timesyncd.service should be present on the image."

    # Check activity and sync when present
    if timedatectl.is_timesyncd_active():
        status = timedatectl.get_timesync_status()
        assert status.ntp, "NTP should be enabled"
        assert status.ntp_synchronized, "NTP should be synchronized"
    else:
        pytest.skip("systemd-timesyncd installed but not active in this environment")


@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("azure")
@pytest.mark.hypervisor("microsoft")
def test_systemd_timesyncd_disabled_on_azure(systemd: Systemd):
    assert (
        systemd.is_active("systemd-timesyncd") == False
    ), f"Chrony instead of systemd-timesyncd should be active on Azure."


@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("azure")
@pytest.mark.hypervisor("microsoft")
def test_chrony_on_azure(systemd: Systemd):
    """
    Test for chrony as active time sync service on Azure.
    See: https://learn.microsoft.com/en-us/azure/virtual-machines/linux/time-sync#chrony
    """
    assert systemd.is_active("chrony"), f"Chrony should be active on Azure."


@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("azure")
@pytest.mark.hypervisor("qemu")
def test_chrony_installed_for_azure_image(systemd: Systemd):
    """
    Test for chrony service installed on Azure image when running in QEMU.
    (no Hyper-V clock available -> chrony is disabled and not loaded)
    """
    units = systemd.list_installed_units()
    chrony_unit = next(
        (unit for unit in units if unit.unit == "chrony.service"),
        None,
    )

    assert chrony_unit is not None, "chrony.service should be presenti n Azure images."
    assert chrony_unit.load in (
        "enabled",
        "disabled",
    ), f"Unexpected chrony.service state: {chrony_unit.load!r}"


@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("not azure and not container")
@pytest.mark.arch("amd64")
def test_clocksource_amd64(systemd_detect_virt: Hypervisor, clocksource: str):
    match systemd_detect_virt:
        case Hypervisor.xen | Hypervisor.qemu:
            expected_clocksource = "tsc"
        case Hypervisor.kvm | Hypervisor.amazon:
            expected_clocksource = "kvm-clock"
        case _:
            assert False, f"unknown hypervisor {systemd_detect_virt}"

    assert clocksource, expected_clocksource


@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("not azure and not container")
@pytest.mark.arch("amd64", "aarch64")
def test_clocksource_arm64_aarch64(systemd_detect_virt: Hypervisor, clocksource: str):
    match systemd_detect_virt:
        case Hypervisor.kvm | Hypervisor.qemu | Hypervisor.amazon:
            expected_clocksource = "arch_sys_counter"
        case _:
            assert False, f"unknown hypervisor {systemd_detect_virt}"

    assert clocksource, expected_clocksource


@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("azure")
@pytest.mark.hypervisor("microsoft")
def test_chrony_azure(
    chrony_config_file: str, ptp_hyperv_dev: str, systemd_detect_virt: Hypervisor
):
    """
    Check Chrony configuration for expected content according to https://learn.microsoft.com/en-us/azure/virtual-machines/linux/time-sync

    Gets skipped for QEMU tests as these do not start chrony.
    """
    expected_config = f"refclock PHC {ptp_hyperv_dev} poll 3 dpoll -2 offset 0"
    with open(chrony_config_file, "r") as f:
        actual_config = f.read()
        assert (
            actual_config.find(expected_config) != -1
        ), f"chrony config for ptp expected but not found"


@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("azure")
@pytest.mark.hypervisor("microsoft")
def test_azure_ptp_symlink(ptp_hyperv_dev: str, systemd_detect_virt: Hypervisor):
    """
    Ensure /dev/ptp_hyperv exists and is a symlink on real Azure VMs.

    Skips for QEMU only provides a generic virtualized clock.
    """
    assert os.path.islink(
        ptp_hyperv_dev
    ), f"{ptp_hyperv_dev} should always be a symlink."


@pytest.mark.parametrize("dir", ["/bin", "/etc/ssh"])
def test_files_not_in_future(dir: str):
    """
    Validate that all files in the image have a timestamp in the past.
    """
    now = datetime.now()
    for root, dirs, filenames in os.walk(dir):
        for filename in filenames:
            file = os.path.join(root, filename)
            modification = datetime.fromtimestamp(os.path.getmtime(file))
            assert (
                modification <= now
            ), f"timestamp of {file} is in the future {modification} (now={now})"
