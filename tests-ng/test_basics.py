import os
import pytest
from plugins.shell import ShellRunner
from plugins.systemd import Systemd


def test_gl_is_support_distro():
    with open("/etc/os-release", "r") as f:
        assert "ID=gardenlinux" in [ line.strip() for line in f], "/etc/os-release does not contain gardenlinux vendor field"

def test_no_man(shell: ShellRunner):
    result = shell("man ls", capture_output=True, ignore_exit_code=True)
    assert result.returncode == 127 and "not found" in result.stderr, "man ls, did not fail with 'not found' as expected"

def test_fhs(shell: ShellRunner):
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

@pytest.mark.booted(reason="We can only measure startup time if we actually boot the system")
@pytest.mark.performance_metric
@pytest.mark.feature("server and not azure") # server installs systemd and azure has notoriously bad startup times
def test_startup_time(systemd: Systemd):
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

@pytest.mark.feature("not gcp and not metal and not openstack", reason='Does not work on gcp, metal and openstack features for various reasons, for example because it cannot communicate with external backends.')
@pytest.mark.root(reason="Needed for journalctl which is only needed when the test fails, but still very useful for understanding test failures")
@pytest.mark.booted(reason="Systemctl needs a booted system")
def test_no_failed_units(systemd: Systemd, shell: ShellRunner):
    units = systemd.list_units()
    assert len(units) > 1, f"Failed to load systemd units: {units}"
    failed_units = [u for u in units if u.load == 'loaded' and u.active != 'active']
    for u in failed_units:
        print(f'FAILED UNIT: {u}')
        shell(f"journalctl --unit {u.unit}")
    assert not failed_units, f"{len(failed_units)} systemd units failed to load"
