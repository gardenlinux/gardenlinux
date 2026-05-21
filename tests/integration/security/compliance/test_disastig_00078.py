"""
Ref: SRG-OS-000184-GPOS-00078

Verify the operating system fails to a secure state if system initialization
fails, shutdown fails, or aborts fail.
"""


def test_kernel_dump_is_disabled():
    with open("/proc/sys/kernel/core_pattern") as fd:
        assert fd.read() == "|/bin/false"
