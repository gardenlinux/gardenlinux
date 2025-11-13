import os

import pytest
from plugins.kernel_configs import KernelConfigs
from plugins.parse_file import ParseFile
from plugins.sysctl import Sysctl


def test_kernel_configs_sysrq_not_set_cloud(
    parse_file: ParseFile, kernel_configs: KernelConfigs
):
    """Test that the kernel config does not set magic sysrq."""
    for config in kernel_configs.get_installed():
        line = "# CONFIG_MAGIC_SYSRQ is not set"
        lines = parse_file.lines(
            config.path,
            comment_char=[],  # Disable comment filtering for kernel config files
        )
        assert line in lines, f"Could not find line {line} in {config.path}."


@pytest.mark.booted(reason="Requires running system")
def test_sysctl_sysrq_not_set(sysctl: Sysctl):
    """Test that sysctl sysrq parameter is not available."""
    assert "kernel.sysrq" not in sysctl


@pytest.mark.booted(reason="Requires running system")
def test_magic_sysrq_trigger_not_exists():
    """Test that sysrq trigger does not exist."""
    assert not os.path.exists("/proc/sysrq-trigger")
