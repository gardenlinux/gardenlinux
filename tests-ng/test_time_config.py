import pytest
import os
from time import time
from datetime import datetime

from plugins.shell import ShellRunner
from plugins.timedatectl import TimeDateCtl, TimeSyncStatus
from plugins.timeconf import clocksource_file, chrony_config_file

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

@pytest.mark.booted(reason="NTP server configuration is read at runtime")
def test_ntp(timedatectl: TimeDateCtl):
    timesyncstatus: TimeSyncStatus = timedatectl.get_timesync_status()
    assert timesyncstatus.ntp, f"NTP not activated"
    assert timesyncstatus.ntp_synchronized, f"NTP not synchronized"

@pytest.mark.skip(reason="xen is no longer activly used")
@pytest.mark.feature("xen")
@pytest.mark.parametrize("expected_clock_source", ["tsc"])
def test_clocksource_xen(clocksource_file: str, expected_clock_source: str):
    """
    Check if clocksource matches this archtectures expected value
    """
    _cmp_clksrc(clocksource_file=clocksource_file, expected=expected_clock_source)

@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("x86_64 and (kvm or aws)")
@pytest.mark.parametrize("expected_clock_source", ["tsc"])
def test_clocksource_kvm_aws_amd64(clocksource_file: str, expected_clock_source: str):
    """
    Check if clocksource matches this archtectures expected value.
    For AWS this is documented here: https://repost.aws/knowledge-center/manage-ec2-linux-clock-source
    """
    _cmp_clksrc(clocksource_file=clocksource_file, expected=expected_clock_source)

@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("(kvm or aws) and (aarch64 or arm64)")
@pytest.mark.parametrize("expected_clock_source", ["arch_sys_counter"])
def test_clocksource_kvm_aws_aarch64(clocksource_file: str, expected_clock_source: str):
    """
    Check if clocksource matches this archtectures expected value.
    For AWS this is documented here: https://repost.aws/knowledge-center/manage-ec2-linux-clock-source
    """
    _cmp_clksrc(clocksource_file=clocksource_file, expected=expected_clock_source)

@pytest.mark.booted(reason="NTP server configuration is read at runtime")
@pytest.mark.feature("azure")
def test_chrony_azure(chrony_config_file: str):
    """
    Check Chrony configuration for expected content
    """
    expected_config = "refclock PHC /dev/ptp_hyperv poll 3 dpoll -2 offset 0"
    with open(chrony_config_file, "r") as f:
        actual_config = f.read()
        assert actual_config.find(expected_config) != -1, f"chrony config for ptp expected but not found"

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

def _cmp_clksrc(clocksource_file: str, expected: str):
    """
    Check clocksource_file for expected content.
    """
    with open(clocksource_file, "r") as f:
        actual = f.read().rstrip()
        assert expected == actual, f"expected {expected} but got '{actual}'"

