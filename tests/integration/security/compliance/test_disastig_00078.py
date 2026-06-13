"""
Ref: SRG-OS-000184-GPOS-00078

Verify the operating system fails to a secure state if system initialization
fails, shutdown fails, or aborts fail.
"""

import pytest


@pytest.mark.feature("disaSTIGmedium")
def test_kernel_dump_is_disabled(sysctl):
    """Verify kernel.core_pattern routes core dumps to /bin/false."""
    assert sysctl["kernel.core_pattern"] == "|/bin/false"
