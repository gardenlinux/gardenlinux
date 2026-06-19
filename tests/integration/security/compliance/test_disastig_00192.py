"""
Ref: SRG-OS-000433-GPOS-00192

Verify the operating system implements non-executable data to protect its
memory from unauthorized code execution.
"""

import pytest


@pytest.mark.security_id(203753)
@pytest.mark.arch("amd64")
def test_nx_bit_hardware_support():
    """Verify /proc/cpuinfo advertises the nx CPU flag (amd64)."""
    with open("/proc/cpuinfo") as cpuinfo:
        assert (
            " nx " in cpuinfo.read()
        ), "Finding: Hardware does not support or report the NX bit."


@pytest.mark.security_id(203753)
@pytest.mark.arch("amd64")
def test_nx_not_disabled_at_boot(kernel_cmdline):
    """Verify nx=off is not present in the kernel boot cmdline."""
    assert (
        "nx=off" not in kernel_cmdline
    ), "Finding: The kernel boot parameter 'nx=off' is present, disabling memory protection."
