import pytest
from plugins.kernel_module import KernelModule


@pytest.mark.booted(reason="Requires running system")
def test_kernel_module_wireguard_available(kernel_module: KernelModule):
    """Test that the wireguard kernel module is available as loadable module."""
    kernel_modules = ["wireguard"]
    for module in kernel_modules:
        assert kernel_module.is_module_available(
            module
        ), f"{module} kernel module is not available."
