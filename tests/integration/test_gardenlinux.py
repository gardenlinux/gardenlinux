import json
import logging
import os
import re
import time
import datetime
from pathlib import Path
from typing import Iterator

import pytest
import yaml

from .aws import AWS
from .gcp import GCP
from .azure import AZURE
from .openstackccee import OpenStackCCEE
from .manual import Manual
from .ali import ALI
from .sshclient import RemoteClient

logger = logging.getLogger(__name__)
giaas = None

@pytest.fixture(scope="module")
def config(configFile):
    try:
        if os.path.exists(configFile):
            realName = configFile
        else:
            root = Path(os.path.dirname(os.path.abspath(__file__))).parent
            realName = root.joinpath(configFile)
        with open(realName) as f:
            options = yaml.load(f, Loader=yaml.FullLoader)
    except OSError as e:
        logger.exception(e)
        exit(1)
    yield options


@pytest.fixture(scope="module")
def client(request, config: dict, iaas) -> Iterator[RemoteClient]:
    logger.info(config)
    if iaas == "aws":
        yield from AWS.fixture(config["aws"])
    elif iaas == "gcp":
        yield from GCP.fixture(config["gcp"])
    elif iaas == "azure":
        yield from AZURE.fixture(config["azure"])
    elif iaas == "openstack-ccee":
        yield from OpenStackCCEE.fixture(config["openstack_ccee"])
    elif iaas == "ali":
        yield from ALI.fixture(config["ali"])
    elif iaas == "manual":
        yield from Manual.fixture(config["manual"])
    else:
        raise ValueError(f"invalid {iaas=}")


@pytest.fixture(scope='module')
def non_ali(iaas):
    if iaas == 'ali':
        pytest.skip('test not supported on ali')

@pytest.fixture(scope='module')
def ali(iaas):
    if iaas != 'ali':
        pytest.skip('test only supported on ali')

@pytest.fixture(scope='module')
def non_azure(iaas):
    if iaas == 'azure':
        pytest.skip('test not supported on azure')

@pytest.fixture(scope='module')
def azure(iaas):
    if iaas != 'azure':
        pytest.skip('test only supported on azure')

@pytest.fixture(scope='module')
def aws(iaas):
    if iaas != 'aws':
        pytest.skip('test only supported on aws')

@pytest.fixture(scope='module')
def gcp(iaas):
    if iaas != 'gcp':
        pytest.skip('test only supported on gcp')

@pytest.fixture(scope='module')
def non_openstack(iaas):
    if iaas == 'openstack-ccee':
        pytest.skip('test not supported on openstack')

@pytest.fixture(scope='module')
def openstack(iaas):
    if iaas != 'openstack-ccee':
        pytest.skip('test only supported on openstack')

@pytest.fixture(scope='module')
def openstack_flavor():
    return OpenStackCCEE.instance().flavor

def test_clock(client):
    (exit_code, output, error) = client.execute_command("date '+%s'")
    local_seconds = time.time()
    assert exit_code == 0, f"no {error=} expected"
    remote_seconds = int(output)
    assert (
        abs(local_seconds - remote_seconds) < 5
    ), "clock skew should be less than 5 seconds. Local time is %s and remote time is %s" % (local_seconds, remote_seconds)

def test_ntp(client, non_azure):
    """azure does not use systemd-timesyncd"""
    (exit_code, output, error) = client.execute_command("timedatectl show")
    assert exit_code == 0, f"no {error=} expected"
    lines = output.splitlines()
    npt_ok=False
    ntp_synchronised_ok=False
    for l in lines:
        nv = l.split("=")
        if nv[0] == "NTP" and nv[1] == "yes":
            ntp_ok = True
        if nv[0] == "NTPSynchronized" and nv[1] == "yes":
            ntp_synchronised_ok = True
    assert ntp_ok, "NTP not activated"
    assert ntp_synchronised_ok, "NTP not synchronized"

def test_ls(client):
    (exit_code, output, error) = client.execute_command("ls /")
    assert exit_code == 0, f"no {error=} expected"
    assert output
    lines = output.split("\n")
    assert "bin" in lines
    assert "boot" in lines
    assert "dev" in lines
    assert "etc" in lines
    assert "home" in lines
    assert "lib" in lines
    assert "lib64" in lines
    assert "mnt" in lines
    assert "opt" in lines
    assert "proc" in lines
    assert "root" in lines
    assert "run" in lines
    assert "sbin" in lines
    assert "srv" in lines
    assert "sys" in lines
    assert "tmp" in lines
    assert "usr" in lines
    assert "var" in lines


def test_no_man(client):
    (exit_code, _, error) = client.execute_command("man ls")
    assert exit_code == 127, '"man" should not be installed'
    assert "man: command not found" in error


def test_metadata_connection_non_az_non_ali(client, non_azure, non_ali):
    metadata_host = "169.254.169.254"
    (exit_code, output, error) = client.execute_command(
        f"wget --timeout 5 http://{metadata_host}"
    )
    assert exit_code == 0, f"no {error=} expected"
    assert f"Connecting to {metadata_host}:80... connected." in error
    assert "200 OK" in error
 

def test_metadata_connection_az(client, azure):

    metadata_url = "http://169.254.169.254/metadata/instance/compute?api-version=2021-01-01&format=json"
    (exit_code, output, error) = client.execute_command(
        f"curl --connect-timeout 5 '{metadata_url}' -H 'Metadata: true'"
    )
    assert exit_code == 0, f"no {error=} expected"

def test_metadate_connection_ali(client, ali):
    metadata_url = "http://100.100.100.200/2016-01-01"
    (exit_code, output, error) = client.execute_command(
        f"curl --connect-timeout 5 '{metadata_url}' -H 'Metadata: true'"
    )
    assert exit_code == 0, f"no {error=} expected"

def test_hostname_azure(client, azure):
    start_time = datetime.datetime.now()
    (exit_code, output, error) = client.execute_command("nslookup $(hostname)")
    assert exit_code == 0, f"no {error=} expected"
    end_time = datetime.datetime.now()
    time_diff = (end_time - start_time)
    execution_time = round(time_diff.total_seconds())
    assert execution_time <= 2, f"nslookup should not run in a timeout {error}"


def test_timesync(client, azure):
    """Ensure symbolic link has been created"""
    (exit_code, output, error) = client.execute_command("test -L /dev/ptp_hyperv")
    assert exit_code == 0, f"Expected /dev/ptp_hyperv to be a symbolic link"

def test_loadavg(client):
    """This test does not produce any load. Make sure no 
       other process does."""
    (exit_code, output, error) = client.execute_command("cat /proc/loadavg")
    assert exit_code == 0, f"Expected to be able to show contents of /proc/loadavg"
    load =  float(output.split(" ")[1])
    assert load  < 0.5, f"Expected load to be less than 0.5 but is {load}"

@pytest.fixture(params=["8.8.8.8", "dns.google", "heise.de"])
def ping4_host(request):
    return request.param


def test_ping4(client, ping4_host):
    command = f"ping -c 5 -W 5 {ping4_host}"
    (exit_code, output, error) = client.execute_command(command)
    assert exit_code == 0, f'no {error=} expected when executing "{command}"'
    assert "5 packets transmitted, 5 received, 0% packet loss" in output


@pytest.fixture(params=["2001:4860:4860::8888", "dns.google", "heise.de"])
def ping6_host(request):
    return request.param

@pytest.mark.skip(reason="ipv6 not available in all vpcs")
def test_ping6(client, ping6_host):
    command = f"ping6 -c 5 -W 5 {ping6_host}"
    (exit_code, output, error) = client.execute_command(command)
    assert exit_code == 0, f'no {error=} expected when executing "{command}"'
    assert "5 packets transmitted, 5 received, 0% packet loss" in output

def test_systemctl_no_failed_units(client):
    (exit_code, output, error) = client.execute_command("systemctl list-units --output=json --state=failed")
    assert exit_code == 0, f"no {error=} expected"
    assert len(json.loads(output)) == 0

def test_startup_time(client):
    tolerated_kernel_time = 15
    tolerated_userspace_time = 30
    (exit_code, output, error) = client.execute_command("systemd-analyze")
    assert exit_code == 0, f"no {error=} expected"
    lines = output.splitlines()
    items = lines[0].split(" ")
    time_initrd = 0
    for i, v in enumerate(items):
        if v == "(kernel)":
            time_kernel = items[i-1]
        if v == "(initrd)":
            time_initrd = items[i-1]
        if v == "(userspace)":
            time_userspace = items[i-1]
    if len(time_kernel) >2 and time_kernel[-2:] == "ms":
        time_kernel = str(float(time_kernel[:-2]) / 1000.0) + "s"
    if len(time_initrd) >2 and time_initrd[-2:] == "ms":
        time_initrd = str(float(time_initrd[:-2]) / 1000.0) + "s"
    tf_kernel = float(time_kernel[:-1]) + float(time_initrd[:-1])
    tf_userspace = float(time_userspace[:-1])
    assert tf_kernel < tolerated_kernel_time, f"startup time in kernel space too long: {tf_kernel} seconds =  but only {tolerated_kernel_time} tolerated."
    assert tf_userspace < tolerated_userspace_time, f"startup time in user space too long: {tf_userspace}seconds but only {tolerated_userspace_time} tolerated."

def test_chrony(client, azure):
    """Test for specific chrony configuration on azure"""
    expected_config = "refclock PHC /dev/ptp_hyperv poll 3 dpoll -2 offset 0"
    (exit_code, output, error) = client.execute_command("cat /etc/chrony/chrony.conf")
    assert exit_code == 0, f"no {error=} expected"
    assert output.find(expected_config) != -1, f"chrony config for ptp expected but not found"

def test_growpart(client, non_openstack):
    (exit_code, output, error) = client.execute_command("df --output=size -BG /")
    assert exit_code == 0, f"no {error=} expected"
    lines = output.splitlines()
    sgb = int(lines[1].strip()[:-1])
    assert sgb == 6, f"partition size expected to be ~6 GB but is {sgb}"

def test_growpart(client, openstack, openstack_flavor):
    """Disk size on OpenStack is only configurable via flavors"""
    disk_size = int(openstack_flavor["disk"])
    expected_disk_size = disk_size - 1
    (exit_code, output, error) = client.execute_command("df --output=size -BG /")
    assert exit_code == 0, f"no {error=} expected"
    lines = output.splitlines()
    sgb = int(lines[1].strip()[:-1])
    assert sgb == expected_disk_size, f"partition size expected to be ~{expected_disk_size} GB but is {sgb}"

def test_docker(client):
    (exit_code, output, error) = client.execute_command("sudo systemctl start docker")
    if exit_code != 0:
        (journal_rc, output, error) = client.execute_command("sudo journactl --no-pager -xu docker.service")
    assert exit_code == 0, f"no {error=} expected"
    (exit_code, output, error) = client.execute_command("sudo docker run --rm  eu.gcr.io/gardenlinux/gardenlinux:184.0 sh -c 'echo from container'")
    assert exit_code == 0, f"no {error=} expected"
    assert output == "from container\n", f"Expected 'from container' output but got {output}"

def test_clocksource(client, aws):
    # kvm or xen
    (exit_code, output, error) = client.execute_command("systemd-detect-virt")
    assert exit_code == 0, f"no {error=} expected"
    hypervisor = output.rstrip()
    (exit_code, output, error) = client.execute_command("cat /sys/devices/system/clocksource/clocksource0/current_clocksource")
    assert exit_code == 0, f"no {error=} expected"
    if hypervisor == "xen":
        assert output.rstrip() == "tsc", f"expected clocksoure for xen to be set to tsc but got {output}"
    elif hypervisor == "kvm" or hypervisor == "amazon":
        assert output.rstrip() == "kvm-clock", f"expected clocksoure for kvm to be set to kvm-clock but got {output}"
    else:
        assert False, f"unknown hypervisor {hypervisor}"

def test_correct_ntp(client, aws):
    (exit_code, output, error) = client.execute_command("grep -c ^NTP=169.254.169.123 /etc/systemd/timesyncd.conf")
    assert exit_code == 0, f"no {error=} expected"
    assert output.rstrip() == "1", "Expected NTP server to be configured to 169.254.169.123"

def test_correct_ntp(client, gcp):
    (exit_code, output, error) = client.execute_command("grep -c ^NTP=metadata.google.internal /etc/systemd/timesyncd.conf")
    assert exit_code == 0, f"no {error=} expected"
    assert output.rstrip() == "1", "Expected NTP server to be configured to metadata.google.internal"

def test_nvme_kernel_parameter(client, aws):
    (exit_code, output, error) = client.execute_command("grep -c nvme_core.io_timeout=4294967295 /proc/cmdline")
    assert exit_code == 0, f"no {error=} expected"
    assert output.rstrip() == "1", "Expected 'nvme_core.io_timeout=4294967295' kernel parameter"

def test_random(client):
    (exit_code, output, error) = client.execute_command("time dd if=/dev/random of=/dev/null bs=8k count=1000 iflag=fullblock")
    """ Output should be like this:
# time dd if=/dev/random of=/dev/null bs=8k count=1000 iflag=fullblock
1000+0 records in
1000+0 records out
8192000 bytes (8.2 MB, 7.8 MiB) copied, 0.0446423 s, 184 MB/s

real    0m0.046s
user    0m0.004s
sys     0m0.042s
"""

    assert exit_code == 0, f"no {error=} expected"
    lines = error.splitlines()
    bycount = lines[2].split(" ")[0]
    assert bycount == "8192000", "byte cound expected to be 8192000 but is %s" % bycount
    real = lines[4].split()[1]
    pt=r'(\d+)m(\d+)'
    m=re.search(pt, real)
    duration = (int(m.group(1)) * 60) + int(m.group(2))
    assert duration == 0, "runtime of test expected to be below one second %s" % m.group(1)

    (exit_code, output, error) = client.execute_command("time rngtest --blockcount=9000  < /dev/random")
    """ Output should be like this:
# time rngtest --blockcount=9000  < /dev/random
rngtest 5
Copyright (c) 2004 by Henrique de Moraes Holschuh
This is free software; see the source for copying conditions.  There is NO warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

rngtest: starting FIPS tests...
rngtest: bits received from input: 180000032
rngtest: FIPS 140-2 successes: 8992
rngtest: FIPS 140-2 failures: 8
rngtest: FIPS 140-2(2001-10-10) Monobit: 1
rngtest: FIPS 140-2(2001-10-10) Poker: 2
rngtest: FIPS 140-2(2001-10-10) Runs: 2
rngtest: FIPS 140-2(2001-10-10) Long run: 3
rngtest: FIPS 140-2(2001-10-10) Continuous run: 0
rngtest: input channel speed: (min=167.311; avg=1321.184; max=1467.191)Mibits/s
rngtest: FIPS tests speed: (min=24.965; avg=138.842; max=145.599)Mibits/s
rngtest: Program run time: 1367504 microseconds

real    0m1.370s
user    0m1.260s
sys     0m0.108s
"""
    # a few test will most certainly always fail, therefore we expect an 
    # error
    # assert exit_code == 0, f"no {error=} expected"
    p_succ=r'rngtest: FIPS 140-2 successes: (\d+)'
    m=re.search(p_succ, error)
    successes = int(m.group(1))
    assert successes >8980, "Number of successes expected to be greater than 8980"

    p_fail=r'rngtest: FIPS 140-2 failures: (\d+)'
    m=re.search(p_fail, error)
    failures = int(m.group(1))
    assert failures <= 20, "Number of failures expected ot be less than or equal to 20"

    assert successes + failures == 9000, "sanity check failed"

    p_real=r'real\s+(\d+)m(\d+)'
    m=re.search(p_real, error)
    duration = (int(m.group(1)) * 60) + int(m.group(2))
    assert duration < 5, "Expected the test to run in less than 5 seconds"

def test_startup_script(client, gcp):
    (exit_code, output, error) = client.execute_command("test -f /tmp/startup-script-ok")
    assert exit_code == 0, f"no {error=} expected. Startup script did not run"

