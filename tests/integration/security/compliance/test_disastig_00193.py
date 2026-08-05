"""
Ref: SRG-OS-000433-GPOS-00193
"""

import pytest
from plugins.sysctl import Sysctl


@pytest.mark.feature("disaSTIGmedium and cloud")
@pytest.mark.booted(reason="requires access to /proc/sys at runtime")
@pytest.mark.root(reason="requires access to kernel parameters")
def test_aslr_is_fully_enabled(sysctl: Sysctl):
    """Verify the operating system implements full address space layout randomization with kernel.randomize_va_space set to 2."""
    assert (
        sysctl["kernel.randomize_va_space"] == 2
    ), "stigcompliance: kernel.randomize_va_space must be 2 (full ASLR)"
