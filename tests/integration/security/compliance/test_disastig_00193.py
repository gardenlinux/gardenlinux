import pytest


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="requires running kernel to read sysctl values")
@pytest.mark.root(reason="requires access to sysctl parameters")
def test_aslr_enabled(sysctl):
    """
    As per DISA STIG compliance requirements, the operating system must implement
    non-executable data to protect its memory from unauthorized code execution.
    This test verifies that Address Space Layout Randomization (ASLR) is fully
    enabled (kernel.randomize_va_space = 2).
    Ref: SRG-OS-000433-GPOS-00193
    """
    value = sysctl["kernel.randomize_va_space"]

    assert value == 2, (
        f"stigcompliance: ASLR not fully enabled "
        f"(kernel.randomize_va_space={value}, expected 2)"
    )
