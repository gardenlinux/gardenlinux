import pytest
import time
from pathlib import Path
from helper.sshclient import RemoteClient


def test_correct_ntp(client, aws):
    """ Test for hyperscaler related NTP server """
    (exit_code, output, error) = client.execute_command("grep -c ^NTP=169.254.169.123 /etc/systemd/timesyncd.conf")
    assert exit_code == 0, f"no {error=} expected"
    assert output.rstrip() == "1", "Expected NTP server to be configured to 169.254.169.123"


def test_correct_ntp(client, gcp):
    """ Test for hyperscaler related NTP server """
    (exit_code, output, error) = client.execute_command("timedatectl show-timesync | grep -c ^SystemNTPServers=metadata.google.internal")
    assert exit_code == 0, f"no {error=} expected"
    assert output.rstrip() == "1", "Expected NTP server to be configured to metadata.google.internal"


def test_timesync(client, azure):
    """ Ensure symbolic link has been created """
    (exit_code, output, error) = client.execute_command("test -L /dev/ptp_hyperv")
    assert exit_code == 0, f"Expected /dev/ptp_hyperv to be a symbolic link"


def test_clock(client):
    """ Test clock skew """
    (exit_code, output, error) = client.execute_command("date '+%s'")
    local_seconds = time.time()
    assert exit_code == 0, f"no {error=} expected"
    remote_seconds = int(output)
    assert (
        abs(local_seconds - remote_seconds) < 5
    ), "clock skew should be less than 5 seconds. Local time is %s and remote time is %s" % (local_seconds, remote_seconds)


def test_ntp(client, non_azure, non_chroot):
    """ Azure does not use systemd-timesyncd """
    (exit_code, output, error) = client.execute_command("timedatectl show")
    assert exit_code == 0, f"no {error=} expected"
    lines = output.splitlines()
    ntp_ok=False
    ntp_synchronised_ok=False
    for l in lines:
        nv = l.split("=")
        if nv[0] == "NTP" and nv[1] == "yes":
            ntp_ok = True
        if nv[0] == "NTPSynchronized" and nv[1] == "yes":
            ntp_synchronised_ok = True
    assert ntp_ok, "NTP not activated"
    assert ntp_synchronised_ok, "NTP not synchronized"


def test_files_not_in_future(client):
    """ Testing for files in future """
    testscript_name="/tmp/filemodtime-test.py"
    testscript='''import os
import sys
from datetime import datetime

now = datetime.now()
dirs = ["/bin", "/etc/ssh"]
for dir in dirs:
    for (dirpath, dirnames, filenames) in os.walk(dir):
        for f in filenames:
            file = os.path.join(dir, f)
            modification = datetime.fromtimestamp(os.path.getmtime(file))
            if modification > now:
                print(f"FAIL - {file}s timestamp is {modification}")
                sys.exit(1)
__EOF
'''
    (exit_code, output, error) = client.execute_command(f"cat << '__EOF'\n{testscript}\n > {testscript_name}")
    assert exit_code == 0, f"no {error=} expected"
    (exit_code, output, error) = client.execute_command(f"python3 {testscript_name}")
    assert exit_code == 0, f"no {error=} expected"
    assert "FAIL" not in output


def test_clocksource(client, aws):
    """ Test for clocksource """
    # refer to https://aws.amazon.com/premiumsupport/knowledge-center/manage-ec2-linux-clock-source/
    # detect hypervisor type kvm or xen
    (exit_code, output, error) = client.execute_command("systemd-detect-virt")
    assert exit_code == 0, f"no {error=} expected"
    hypervisor = output.rstrip()
    # which architecture are we on?
    (exit_code, output, error) = client.execute_command("uname -m")
    assert exit_code == 0, f"no {error=} expected"
    arch = output.rstrip()
    # check clock_source
    (exit_code, output, error) = client.execute_command("cat /sys/devices/system/clocksource/clocksource0/current_clocksource")
    assert exit_code == 0, f"no {error=} expected"
    if hypervisor == "xen":
        assert output.rstrip() == "tsc", f"expected clocksoure for xen to be set to tsc but got {output}"
    elif hypervisor == "kvm" or hypervisor == "amazon":
        if arch == "aarch64":
            assert output.rstrip() == "arch_sys_counter", f"expected clocksoure on ARM64 to be set to arch_sys_counter-clock but got {output}"
        else:
            assert output.rstrip() == "kvm-clock", f"expected clocksoure for kvm to be set to kvm-clock but got {output}"
    else:
        assert False, f"unknown hypervisor {hypervisor}"


def test_chrony(client, azure):
    """ Test for specific chrony configuration on azure """
    expected_config = "refclock PHC /dev/ptp_hyperv poll 3 dpoll -2 offset 0"
    (exit_code, output, error) = client.execute_command("cat /etc/chrony/chrony.conf")
    assert exit_code == 0, f"no {error=} expected"
    assert output.find(expected_config) != -1, f"chrony config for ptp expected but not found"
