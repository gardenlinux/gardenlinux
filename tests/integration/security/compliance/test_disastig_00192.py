import pytest

"""
Ref: SRG-OS-000433-GPOS-00192

Verify the operating system implements non-executable data to protect its
memory from unauthorized code execution.
"""

# Note: for arm arch XN (execute never) feature is always present


@pytest.mark.arch("amd64")
def test_nx_bit_hardware_support():
    """Verify hardware supports Non-Executable (NX) memory."""
    with open("/proc/cpuinfo") as cpuinfo:
        assert (
            " nx " in cpuinfo.read()
        ), "Finding: Hardware does not support or report the NX bit."


@pytest.mark.arch("amd64")
def test_nx_not_disabled_at_boot():
    """Verify the kernel has not been explicitly told to disable NX."""
    with open("/proc/cmdline") as cmdline:
        assert (
            "nx=off" not in cmdline.read()
        ), "Finding: The kernel boot parameter 'nx=off' is present, disabling memory protection."
