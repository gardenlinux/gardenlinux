import glob
import os
from typing import List

import pytest


@pytest.mark.feature("server")
@pytest.mark.booted(reason="sysfs knobs are applied at boot")
def test_cpu_performance(kernel_cmdline: List[str]):
    assert "intel_idle.max_cstate=1" in kernel_cmdline
    assert "processor.max_cstate=1" in kernel_cmdline

    def read(path):
        with open(path) as f:
            return f.read().strip()

    for policy in glob.glob("/sys/devices/system/cpu/cpufreq/policy*"):
        if os.path.exists(f"{policy}/scaling_governor"):
            assert read(f"{policy}/scaling_governor") == "performance"
        if os.path.exists(f"{policy}/energy_performance_preference"):
            assert read(f"{policy}/energy_performance_preference") == "performance"

    for cpu in glob.glob("/sys/devices/system/cpu/cpu[0-9]*"):
        if os.path.exists(f"{cpu}/power/energy_perf_bias"):
            assert read(f"{cpu}/power/energy_perf_bias") == "0"
