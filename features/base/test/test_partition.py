import pytest
from helper.sshclient import RemoteClient


def test_growpart(client, non_openstack):
    """ Test for an expected partition size around 6GB """
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
