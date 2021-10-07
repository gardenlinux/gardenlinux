import json
import logging
import os
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
    else:
        raise ValueError(f"invalid {iaas=}")


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
    ), "clock skew should be less than 5 seconds"


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


def test_metadata_connection_non_az(client, non_azure):
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
    assert exit_code == 0, f"no {error=} expected"
    (exit_code, output, error) = client.execute_command("sudo docker run --rm  alpine:3.14.2 sh -c 'echo from container'")
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
    elif hypervisor == "kvm":
        assert output.rstrip() == "kvm-clock", f"expected clocksoure for kvm to be set to kvm-clock but got {output}"
    else:
        assert False, f"unknown hypervisor {hypervisor}"

def test_correct_ntp(client, aws):
    (exit_code, output, error) = client.execute_command("grep -c ^NTP=169.254.169.123 /etc/systemd/timesyncd.conf")
    assert exit_code == 0, f"no {error=} expected"
    assert output.rstrip() == "1", "Expected NTP server to be configured to 169.254.169.123"

def test_nvme_kernel_parameter(client, aws):
    (exit_code, output, error) = client.execute_command("grep -c nvme_core.io_timeout=4294967295 /proc/cmdline")
    assert exit_code == 0, f"no {error=} expected"
    assert output.rstrip() == "1", "Expected 'nvme_core.io_timeout=4294967295' kernel parameter"
