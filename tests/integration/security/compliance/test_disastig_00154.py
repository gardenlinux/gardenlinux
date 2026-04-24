import pytest


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="requires running system to check LSM state")
@pytest.mark.root(reason="requires access to system security configuration")
def test_selinux_is_installed(lsm):
    """
    As per DISA STIG compliance requirements, the operating system must prevent
    the installation of patches, service packs, device drivers, or operating
    system components without verification they have been digitally signed using
    a certificate that is recognized and approved by the organization.
    This test verifies that SELinux is present as the mandatory access control
    mechanism on the system.
    Ref: SRG-OS-000368-GPOS-00154
    """
    assert (
        "selinux" in lsm
    ), "stigcompliance: SELinux is not installed or not active as LSM"
