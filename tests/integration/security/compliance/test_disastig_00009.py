import pytest


@pytest.mark.feature("not container and not lima and not gardener and not baremetal")
@pytest.mark.root(reason="required to verify PAM authentication enforcement")
def test_session_lock_requires_reauthentication(lsm):
    """
    As per DISA STIG compliance requirements, the operating system must retain a
    user's session lock until that user reestablishes access using established
    identification and authentication procedures.
    This test verifies that PAM configuration enforces authentication using
    standard authentication modules and does not allow bypass mechanisms.
    Ref: SRG-OS-000028-GPOS-00009
    """

    assert (
        "selinux" in lsm
    ), "stigcompliance: no LSM (AppArmor/SELinux) present to enforce session lock re-authentication"
