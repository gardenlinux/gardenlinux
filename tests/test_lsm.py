from typing import List

import pytest
from plugins.file import File


# SELinux
@pytest.mark.testcov(["GL-TESTCOV-_selinux-config-kernel-cmdline-lsm"])
@pytest.mark.feature("_selinux")
@pytest.mark.booted(reason="requires a running kernel to read /proc/cmdline")
def test_selinux_cmdline(kernel_cmdline: List[str]):
    assert "security=selinux" in kernel_cmdline


@pytest.mark.feature("_selinux")
@pytest.mark.booted(reason="requires a running kernel to access sysfs")
def test_selinux_enabled(file: File):
    assert file.exists("/sys/fs/selinux/enforce"), "SELinux not enabled"


@pytest.mark.testcov(["GL-TESTCOV-_selinux-config-kernel-cmdline-lsm"])
@pytest.mark.booted
@pytest.mark.feature("_selinux")
def test_lsm_selinux(lsm):
    assert "selinux" in lsm
    assert "apparmor" not in lsm


# Apparmor
@pytest.mark.testcov(["GL-TESTCOV-gardener-config-kernel-cmdline-lsm"])
@pytest.mark.feature("gardener")
@pytest.mark.booted(reason="requires a running kernel to read /proc/cmdline")
def test_apparmor_cmdline(kernel_cmdline: List[str]):
    assert "security=apparmor" in kernel_cmdline


@pytest.mark.testcov(["GL-TESTCOV-gardener-config-kernel-cmdline-lsm"])
@pytest.mark.booted
@pytest.mark.feature("gardener")
def test_lsm_gardener(lsm):
    assert "apparmor" in lsm
    assert "selinux" not in lsm


@pytest.mark.booted
def test_lsm_common(lsm):
    required = {"landlock", "lockdown", "capability", "yama"}
    missing = required - set(lsm)
    assert not missing, f"missing lsm(s): {', '.join(sorted(missing))}"
