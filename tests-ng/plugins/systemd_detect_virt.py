from enum import Enum

import pytest
from plugins.shell import ShellRunner


class Hypervisor(Enum):
    """
    ids according to https://www.freedesktop.org/software/systemd/man/latest/systemd-detect-virt.html
    """

    none = 0
    qemu = 1
    kvm = 2
    amazon = 3
    zvm = 4
    vmware = 5
    microsoft = 6
    oracle = 7
    powervm = 8
    xen = 9
    bochs = 10
    uml = 11
    parallels = 12
    hbyve = 13
    qnx = 14
    acrn = 15
    apple = 16
    sre = 17
    google = 18


@pytest.fixture
def systemd_detect_virt(shell: ShellRunner) -> Hypervisor:
    result = shell(cmd="systemd-detect-virt -v", capture_output=True)
    return Hypervisor[result.stdout.strip()]
