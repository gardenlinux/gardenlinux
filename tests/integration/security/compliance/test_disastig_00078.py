import pytest

"""
Ref: SRG-OS-000184-GPOS-00078

Verify the operating system fails to a secure state if system initialization
fails, shutdown fails, or aborts fail.
"""


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="sysctl values are only applied on a booted system")
def test_kernel_dump_is_disabled(sysctl):
    assert sysctl["kernel.core_pattern"] == "|/bin/false"
