"""
Ref: SRG-OS-000312-GPOS-00154

As per DISA STIG compliance requirements, the operating system must implement
mandatory access controls to restrict the ability of subjects and objects from
accessing resources.
"""

import pytest


@pytest.mark.security_id(203721)
@pytest.mark.feature("_selinux")
@pytest.mark.booted(reason="requires booted system to verify LSM enforcement")
@pytest.mark.root(reason="requires access to system security configuration")
def test_selinux_is_active_lsm(lsm):
    """Verify 'selinux' is reported in the active LSM list."""
    assert (
        "selinux" in lsm
    ), "stigcompliance: SELinux is not listed as an active Linux Security Module"
