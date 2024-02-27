import pytest
import helper.utils as utils


@pytest.mark.parametrize(
    "kernel_config_item",
    [
        "CONFIG_X86_SGX",
        "CONFIG_X86_SGX_KVM",
    ]
)
def test_kernel_configs_enabled(client, kernel_config_item):
    kernel_config_paths = utils.get_kernel_config_paths(client)
    for kconf in kernel_config_paths:
        assert utils.check_kernel_config_enabled(client, kconf, kernel_config_item), f"Kernel Config: {kernel_config_item} is not set, but expected it to be set to y or m"

@pytest.mark.parametrize(
    "kernel_config_item",
    [
        "CONFIG_REMOTEPROC",
        "CONFIG_MAGIC_SYSRQ",
    ]
)
def test_kernel_configs_disabled(client, kernel_config_item):
    kernel_config_paths = utils.get_kernel_config_paths(client)
    for kconf in kernel_config_paths:
        assert not utils.check_kernel_config_enabled(client, kconf, kernel_config_item), f"Kernel Config: {kernel_config_item} is set, but expected it to be disabled or not set"
