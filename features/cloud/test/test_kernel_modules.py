import pytest
import helper.utils as utils
import glob
import sys
import os

@pytest.mark.parametrize(
    "module_name",
    [
        "wireguard"
    ]
)

def test_kernel_modules(client, module_name):
    """Check if the module_name kernel module is available as loadable module """
    # NOTE: check all kernel versions, in case multiple kernels are installed
    assert utils.check_module_exists_in_all_kernels(client, module_name), f"{module_name} does not exist in image"

