import pytest
from helper.utils import get_architecture
from helper.sshclient import RemoteClient


def test_no_man(client):
    """ Test that no man files are present """
    (exit_code, _, error) = client.execute_command("man ls", disable_sudo=True)
    assert exit_code == 127, '"man" should not be installed'
    assert "man: command not found" in error


def test_loadavg(client, non_kvm, non_chroot):
    """ This test does not produce any load. Make sure no other process does """
    (exit_code, output, error) = client.execute_command("cat /proc/loadavg")
    assert exit_code == 0, f"Expected to be able to show contents of /proc/loadavg"
    load =  float(output.split(" ")[1])
    assert load  < 0.5, f"Expected load to be less than 0.5 but is {load}"


def test_ls(client):
    """ Test for regular linux folders/mounts """
    (exit_code, output, error) = client.execute_command("ls /")
    assert exit_code == 0, f"no {error=} expected"
    assert output
    arch = get_architecture(client)
    lines = output.split("\n")
    assert "bin" in lines
    assert "boot" in lines
    assert "dev" in lines
    assert "etc" in lines
    assert "home" in lines
    assert "lib" in lines
    if arch == "amd64":
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


def test_startup_time(client, non_chroot, non_kvm):
    """ Test for startup time """
    tolerated_kernel_time = 15
    tolerated_userspace_time = 40
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


def test_startup_script(client, gcp):
    """ Test for validity of startup script on gcp """
    (exit_code, output, error) = client.execute_command("test -f /tmp/startup-script-ok")
    assert exit_code == 0, f"no {error=} expected. Startup script did not run"
