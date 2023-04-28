import pytest
from helper.utils import get_architecture
from helper.sshclient import RemoteClient


def test_startup_time(client, non_chroot, non_kvm):
    """ Test for startup time """
    tolerated_kernel_time = 15
    tolerated_userspace_time = 60
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

def test_loadavg(client, non_kvm, non_chroot):
    """ This test does not produce any load. Make sure no other process does """
    (exit_code, output, error) = client.execute_command("cat /proc/loadavg")
    assert exit_code == 0, f"Expected to be able to show contents of /proc/loadavg"
    load =  float(output.split(" ")[1])
    assert load  < 0.8, f"Expected load to be less than 0.8 but is {load}"
