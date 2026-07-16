from typing import List

import pytest

from .booted import is_system_booted


@pytest.fixture
def lsm() -> List[str]:
    if not is_system_booted():
        pytest.skip("can't access sysfs when not running on a booted system")
    with open("/sys/kernel/security/lsm", "r") as f:
        return [s.strip() for s in f.read().strip().split(",") if s.strip()]
