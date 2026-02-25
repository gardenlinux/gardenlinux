from typing import List

import pytest

from .booted import is_system_booted


@pytest.fixture
def kernel_cmdline() -> List[str]:
    if not is_system_booted():
        pytest.skip("can't get kernel cmdline when not running on a booted system")
    with open("/proc/cmdline", "r") as f:
        return f.read().strip().split()
