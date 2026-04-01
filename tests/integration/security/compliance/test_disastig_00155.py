import pytest


@pytest.mark.feature("not container and not gardener")
@pytest.mark.booted(reason="requires booted system to verify LSM enforcement")
@pytest.mark.root(reason="requires access to system security configuration")
def test_deny_all_execution_mechanism_present(shell):
    """
    As per DISA STIG compliance requirements, the operating system must employ a
    deny-all, permit-by-exception policy to allow the execution of authorized
    software programs.
    This test verifies that a Linux Security Module (LSM) capable of enforcing
    execution control (AppArmor or SELinux) is present on the system.
    Ref: SRG-OS-000370-GPOS-00155
    """
    result = shell("cat /sys/kernel/security/lsm", capture_output=True)

    assert (
        result.returncode == 0
    ), "stigcompliance: unable to determine active LSM modules"

    lsm = result.stdout.strip()

    assert (
        "selinux" in lsm
    ), "stigcompliance: no enforcement mechanism (SELinux) present for execution control"
