import pytest


@pytest.mark.feature("_selinux")
@pytest.mark.booted(reason="requires booted system to verify LSM enforcement")
@pytest.mark.root(reason="requires access to system security configuration")
def test_selinux_is_active_lsm(lsm):
    """
    As per DISA STIG compliance requirements, the operating system must implement
    mandatory access controls to restrict the ability of subjects and objects from
    accessing resources.
    This test verifies that SELinux is active as a Linux Security Module.
    Ref: SRG-OS-000312-GPOS-00154
    """
    assert (
        "selinux" in lsm
    ), "stigcompliance: SELinux is not listed as an active Linux Security Module"
