import os
from typing import List

import pytest
from plugins.sysctl import Sysctl


@pytest.mark.feature("dbPerf")
@pytest.mark.booted(reason="runtime knobs are applied at boot")
def test_dbperf_memory(sysctl: Sysctl, kernel_cmdline: List[str]):
    assert sysctl["kernel.numa_balancing"] == 0
    assert sysctl["vm.dirty_bytes"] == 629145600
    assert sysctl["vm.dirty_background_bytes"] == 314572800
    assert sysctl["fs.aio-max-nr"] == 18446744073709551615
    assert sysctl["net.ipv4.tcp_slow_start_after_idle"] == 0

    assert "tsx=auto" in kernel_cmdline
    assert "numa_balancing=disable" in kernel_cmdline
    assert "transparent_hugepage=madvise" in kernel_cmdline

    def read(path):
        with open(path) as f:
            return f.read().strip()

    # Cross-check the effective values in sysfs on top of the cmdline args,
    # skipping nodes that do not exist on this kernel/arch.
    thp_enabled = "/sys/kernel/mm/transparent_hugepage/enabled"
    if os.path.exists(thp_enabled):
        assert "[madvise]" in read(thp_enabled)

    numa_balancing = "/proc/sys/kernel/numa_balancing"
    if os.path.exists(numa_balancing):
        assert read(numa_balancing) == "0"
