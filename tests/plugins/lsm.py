from typing import List

import pytest

from .booted import is_system_booted


def active_lsms():
    with open("/sys/kernel/security/lsm", "r") as f:
        return [s.strip() for s in f.read().strip().split(",") if s.strip()]


@pytest.fixture
def lsm() -> List[str]:
    if not is_system_booted():
        pytest.skip("can't access sysfs when not running on a booted system")
    return active_lsms()


@pytest.fixture
def selinux_enforce() -> bool:
    if not is_system_booted():
        pytest.skip("can't access sysfs when not running on a booted system")
    if "selinux" not in active_lsms():
        pytest.skip("can only check on selinux enabled system")
    with open("/sys/fs/selinux/enforce", "r") as f:
        if f.read().strip() != "1":
            pytest.skip("can only check on selinux enforced system")
        else:
            return False
