import pytest

"""
Ref: SRG-OS-000433-GPOS-00192

Verify the operating system implements non-executable data to protect its
memory from unauthorized code execution.
"""


@pytest.mark.arch("amd64")
def test_nx_bit_hardware_support():
    """
    Verify hardware supports Non-Executable (NX) memory.
    Note: for arm architecture XN (execute never) feature is always present.
    """
    with open("/proc/cpuinfo") as cpuinfo:
        assert (
            " nx " in cpuinfo.read()
        ), "Finding: Hardware does not support or report the NX bit."


@pytest.mark.arch("amd64")
def test_nx_not_disabled_at_boot(kernel_cmdline):
    """Verify the kernel has not been explicitly told to disable NX."""
    assert (
        "nx=off" not in kernel_cmdline
    ), "Finding: The kernel boot parameter 'nx=off' is present, disabling memory protection."
