import pytest


@pytest.mark.feature(
    "not container and not gardener and not lima and not capi and not baremetal"
)
@pytest.mark.booted(reason="requires booted system to verify LSM enforcement")
@pytest.mark.root(reason="requires access to system security configuration")
def test_deny_all_execution_mechanism_present(lsm):
    """
    As per DISA STIG compliance requirements, the operating system must employ a
    deny-all, permit-by-exception policy to allow the execution of authorized
    software programs.
    This test verifies that a Linux Security Module (LSM) capable of enforcing
    execution control (AppArmor or SELinux) is present on the system.
    Ref: SRG-OS-000370-GPOS-00155
    """
    assert (
        "selinux" in lsm
    ), "stigcompliance: no enforcement mechanism (SELinux) present for execution control"
