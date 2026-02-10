import os

import pytest
from plugins.file import File
from plugins.parse_file import ParseFile
from plugins.shell import ShellRunner
from plugins.systemd import Systemd


@pytest.mark.setting_ids(["GL-SET-base-config-os-release"])
def test_gl_is_support_distro(parse_file: ParseFile):
    lines = parse_file.lines("/etc/os-release")
    assert (
        "ID=gardenlinux" in lines
    ), "/etc/os-release does not contain gardenlinux vendor field"


@pytest.mark.setting_ids(["GL-SET-_slim-config-no-docs-002"])
def test_no_man(shell: ShellRunner):
    result = shell("man ls", capture_output=True, ignore_exit_code=True)
    assert result.returncode == 127 and (
        "not found" in result.stderr or "Permission denied" in result.stderr
    ), f"man ls did not fail as expected, got: {result.stderr}"


@pytest.mark.parametrize(
    "dir",
    [
        "/boot",
        "/dev",
        "/etc",
        "/home",
        "/mnt",
        "/opt",
        "/proc",
        "/root",
        "/run",
        "/srv",
        "/sys",
        "/tmp",
        "/usr",
        "/var",
    ],
)
def test_fhs_directories(file: File, dir: str):
    assert file.is_dir(f"{dir}"), f"expected FHS directory {dir} does not exist"


@pytest.mark.parametrize(
    "link,target",
    [
        ("/bin", "/usr/bin"),
        ("/lib", "/usr/lib"),
        ("/sbin", "/usr/sbin"),
    ],
)
def test_fhs_symlinks(file: File, link: str, target: str):
    assert file.is_symlink(
        link, target=target
    ), f"expected FHS symlink {link} does not exist"


@pytest.mark.arch("amd64", reason="links only present on amd64")
@pytest.mark.parametrize(
    "link,target",
    [
        ("/lib64", "/usr/lib64"),
    ],
)
def test_fhs_symlinks_amd64(file: File, link: str, target: str):
    assert file.is_symlink(
        link, target=target
    ), f"expected FHS symlink {link} does not exist"


@pytest.mark.booted(
    reason="We can only measure startup time if we actually boot the system"
)
@pytest.mark.performance_metric
def test_startup_time(systemd: Systemd):
    tolerated_kernel = 60.0
    tolerated_userspace = 60.0

    firmware, loader, kernel, initrd, userspace = systemd.analyze()
    kernel_total = kernel + initrd

    assert kernel_total < tolerated_kernel, (
        f"Kernel+initrd startup too slow: {kernel_total:.1f}s "
        f"(tolerated {tolerated_kernel}s)"
    )
    assert userspace < tolerated_userspace, (
        f"Userspace startup too slow: {userspace:.1f}s "
        f"(tolerated {tolerated_userspace}s)"
    )


@pytest.mark.booted(reason="Kernel test makes sense only on booted system")
@pytest.mark.hypervisor(
    "not qemu",
    reason="check if the kernel is tainted only on non qemu tests - https://github.com/gardenlinux/gardenlinux/issues/4103",
)
def test_kernel_not_tainted():
    with open("/proc/sys/kernel/tainted", "r") as f:
        tainted = f.read().strip()
    assert tainted == "0", f"Kernel is tainted (value: {tainted})"


@pytest.mark.feature(
    "not gcp and not metal and not openstack",
    reason="Not compatible, usually because of missing external backends",
)
@pytest.mark.root(reason="Required for journalctl in case of errors")
@pytest.mark.booted(reason="Systemctl needs a booted system")
def test_no_failed_units(systemd: Systemd, shell: ShellRunner):
    system_run_state = systemd.wait_is_system_running()
    print(
        f"Waiting for systemd to report the system is running took {system_run_state.elapsed_time:.2f} seconds, with state '{system_run_state.state}' and return code '{system_run_state.returncode}'."
    )
    failed_systemd_units = systemd.list_failed_units()
    for u in failed_systemd_units:
        print(f"FAILED UNIT: {u}")
        shell(f"journalctl --unit {u.unit}")
    assert (
        not failed_systemd_units
    ), f"{len(failed_systemd_units)} systemd units failed to load"
