import pytest
from plugins.sysctl import Sysctl


@pytest.mark.feature("disaSTIGmedium and cloud")
@pytest.mark.booted(reason="requires access to /proc/sys at runtime")
@pytest.mark.root(reason="requires access to kernel parameters")
def test_aslr_is_fully_enabled(sysctl: Sysctl):
    """
    As per DISA STIG compliance requirements, the operating system must implement
    address space layout randomization (ASLR) to protect memory from unauthorized
    code execution.
    This test verifies that kernel.randomize_va_space is set to 2 (full ASLR).
    Ref: SRG-OS-000433-GPOS-00193
    """
    assert (
        sysctl["kernel.randomize_va_space"] == 2
    ), "stigcompliance: kernel.randomize_va_space must be 2 (full ASLR)"
