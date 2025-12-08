import os

import pytest
from plugins.file import File
from plugins.kernel_configs import KernelConfigs
from plugins.parse_file import FileContent
from plugins.sysctl import Sysctl


def test_kernel_configs_sysrq_not_set_cloud(
    file_content: FileContent, kernel_configs: KernelConfigs
):
    """Test that the kernel config does not set magic sysrq."""
    for config in kernel_configs.get_installed():
        line = "# CONFIG_MAGIC_SYSRQ is not set"
        found = file_content.check_line(
            config.path,
            line,
        )
        assert found, f"Could not find line {line} in {config.path}."


@pytest.mark.booted(reason="Requires running system")
def test_sysctl_sysrq_not_set(sysctl: Sysctl):
    """Test that sysctl sysrq parameter is not available."""
    assert "kernel.sysrq" not in sysctl


@pytest.mark.booted(reason="Requires running system")
def test_magic_sysrq_trigger_not_exists(file: File):
    """Test that sysrq trigger does not exist."""
    assert not file.exists("/proc/sysrq-trigger")
