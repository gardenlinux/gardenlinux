import pytest
import helper.utils as utils
import sys


@pytest.mark.parametrize(
    "test_kernel_config_tuple",
    [
        ("CONFIG_X86_SGX", "y", "enable SGX","amd64"),
        ("CONFIG_X86_SGX_KVM", "y", "enable SGX", "amd64"),
        ("CONFIG_MAGIC_SYSRQ", "n", "Security: an attacker with physical access could use this magic sysrq key to reboot, shutdown or remount", "all"),
       # ("CONFIG_BLK_DEV_RAM_COUNT", "16", "Example how to test for other values than y,m,n", "all"),
    ]
)
def test_kernel_configs(client, test_kernel_config_tuple):
    kernel_config_paths = utils.get_kernel_config_paths(client)
    kernel_conf_key = test_kernel_config_tuple[0]
    kernel_conf_value = test_kernel_config_tuple[1]
    kernel_conf_test_rational = test_kernel_config_tuple[2]
    arch = test_kernel_config_tuple[3]

    for kconf in kernel_config_paths:
        if arch in kconf or arch == "all": 
            if kernel_conf_value == "n":
                print(f"Check if {kernel_conf_key} is disabled for {arch}")
                assert not utils.check_kernel_config_exact(client, kconf, f"{kernel_conf_key}=(y|m)"), f"Kernel Config: {kernel_conf_key} is set, but expected it to be disabled or not set"
            else:
                print(f"Check if {kernel_conf_key} is enabled for {arch}")
                assert utils.check_kernel_config_exact(client, kconf, f"{kernel_conf_key}={kernel_conf_value}"), f"Kernel Config: {kernel_config_item} is not set to {kernel_conf_value}"
        else:
            print(f"Skipping config test of {kernel_conf_key} for architecture {arch}")

