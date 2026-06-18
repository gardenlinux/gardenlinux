import pytest

"""
Ref: SRG-OS-000028-GPOS-00009

Verify the operating system retains a user's session lock until that user
reestablishes access using established identification and authentication
procedures.
"""


@pytest.mark.security_id(203598)
@pytest.mark.feature("not container and not lima and not gardener and not baremetal")
@pytest.mark.root(reason="required to verify PAM authentication enforcement")
def test_session_lock_requires_reauthentication(lsm):
    assert (
        "selinux" in lsm
    ), "stigcompliance: no LSM (AppArmor/SELinux) present to enforce session lock re-authentication"
