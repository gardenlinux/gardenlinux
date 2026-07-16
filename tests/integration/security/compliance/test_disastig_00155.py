"""
Ref: SRG-OS-000370-GPOS-00155

Verify the operating system employs a deny-all, permit-by-exception policy to
allow the execution of authorized software programs.
"""

import pytest


@pytest.mark.feature(
    "not container and not gardener and not lima and not capi and not baremetal"
)
@pytest.mark.security_id(203722)
@pytest.mark.booted(reason="requires booted system to verify LSM enforcement")
@pytest.mark.root(reason="requires access to system security configuration")
def test_deny_all_execution_mechanism_present(lsm):
    """Verify 'selinux' appears in the active LSM list."""
    assert (
        "selinux" in lsm
    ), "stigcompliance: no enforcement mechanism (SELinux) present for execution control"
