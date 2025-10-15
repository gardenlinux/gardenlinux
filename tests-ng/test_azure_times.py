import pytest
from plugins.systemd import Systemd

@pytest.mark.booted(reason="Test runs systemd")
@pytest.mark.root(reason="To start the systemd service")
@pytest.mark.modify(reason="Starts systemd service")
@pytest.mark.performance_metric
@pytest.mark.feature("azure", reason="Azure instance to test boot time for kernel, initrd and userspace") 
def test_startup_time(systemd: Systemd):
    """System startup time must be within tolerated limits."""
    tolerated_kernel = 30.0
    tolerated_userspace = 60.0

    kernel, initrd, userspace = systemd.analyze()
    kernel_total = kernel + initrd

    assert kernel_total < tolerated_kernel, (
        f"Kernel+initrd startup took too long: {kernel_total:.1f}s "
        f"(limit {tolerated_kernel}s)"
    )
    assert userspace < tolerated_userspace, (
        f"Userspace startup took too long: {userspace:.1f}s "
        f"(limit {tolerated_userspace}s)"
    )