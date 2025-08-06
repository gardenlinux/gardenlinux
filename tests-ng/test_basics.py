import os
import pytest

def test_gl_is_support_distro():
    with open("/etc/os-release", "r") as f:
        assert "ID=gardenlinux" in [ line.strip() for line in f], "/etc/os-release does not contain gardenlinux vendor field"

def test_no_man(shell):
    result = shell("man ls", capture_output=True, ignore_exit_code=True)
    assert result.returncode == 127 and "not found" in result.stderr, "man ls, did not fail with 'not found' as expected"

def test_fhs(shell):
    expected_dirs = {
        "bin",
        "boot",
        "dev",
        "etc",
        "home",
        "lib",
        "mnt",
        "opt",
        "proc",
        "root",
        "run",
        "sbin",
        "srv",
        "sys",
        "tmp",
        "usr",
        "var"
    }

    if os.uname().machine == "x86_64":
        expected_dirs.add("lib64")

    for dir in sorted(expected_dirs):
        assert os.path.isdir(f"/{dir}"), f"expected FHS directory /{dir} does not exist"

@pytest.mark.booted
@pytest.mark.performance_metric
@pytest.mark.feature("server and not azure") # server installs systemd and azure has notoriously bad startup times
def test_startup_time(systemd):
    tolerated_kernel = 60.0
    tolerated_userspace = 40.0

    kernel, initrd, userspace = systemd.analyze()
    kernel_total = kernel + initrd

    assert kernel_total < tolerated_kernel, (
        f"Kernel+initrd startup too slow: {kernel_total:.1f}s "
        f"(tolerated {tolerated_kernel}s)"
    )
    assert userspace < tolerated_userspace, (
        f"Userspace startup too slow: {userspace:.1f}s "
        f"(tolerated {tolerated_userspace}s)"
    )
