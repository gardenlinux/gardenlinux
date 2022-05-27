import pytest
from helper.tests.kernel_modules import kernel_modules

@pytest.mark.parametrize(
    "kernel_module",
    [
        "net/wireguard/wireguard.ko"
    ]
)

def test_kernel_modules(client, kernel_module, non_chroot):
     kernel_modules(client, kernel_module)
