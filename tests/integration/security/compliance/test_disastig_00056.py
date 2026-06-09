import pytest

"""
Ref: SRG-OS-000109-GPOS-00056

Verify the operating system locks the root account. A locked root account
prevents direct login as root, forcing administrators to use privilege
escalation mechanisms instead.
"""


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-root-locked"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="root account locking is enforced by disaSTIGmedium"
)
@pytest.mark.security_id(203644)
@pytest.mark.root(reason="requires root to read shadow password status")
def test_root_account_is_locked(shell) -> None:
    """Verify root account is locked (field 2 of passwd --status output is 'L')."""
    result = shell("passwd --status root", capture_output=True, ignore_exit_code=True)
    fields = result.stdout.split()
    assert (
        len(fields) >= 2 and fields[1] == "L"
    ), f"stigcompliance: root account is not locked (passwd --status output: {result.stdout!r})"
