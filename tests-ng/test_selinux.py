import os
from typing import List

import pytest


@pytest.mark.feature("_selinux")
@pytest.mark.booted(reason="requires a running kernel to read /proc/cmdline")
def test_selinux_cmdline(kernel_cmdline: List[str]):
    assert "security=selinux" in kernel_cmdline


@pytest.mark.feature("_selinux")
@pytest.mark.booted(reason="requires a running kernel to access sysfs")
def test_selinux_enabled():
    assert os.path.exists("/sys/fs/selinux/enforce"), "SELinux not enabled"
