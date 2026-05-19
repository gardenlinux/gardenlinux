import pytest

"""
Ref: SRG-OS-000373-GPOS-00156

Verify the operating system requires users to reauthenticate for privilege
escalation. The sudoers wheel file must exist and be empty so that wheel-group
membership does not grant passwordless sudo.
"""

SUDOERS_WHEEL = "/etc/sudoers.d/wheel"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-sudoers-wheel"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="sudoers wheel truncation is applied by disaSTIGmedium"
)
def test_sudoers_wheel_file_exists(file) -> None:
    """Verify /etc/sudoers.d/wheel exists (created/truncated by disaSTIGmedium)."""
    assert file.exists(SUDOERS_WHEEL), f"stigcompliance: {SUDOERS_WHEEL} does not exist"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-sudoers-wheel"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="sudoers wheel truncation is applied by disaSTIGmedium"
)
def test_sudoers_wheel_file_is_empty(file) -> None:
    """Verify /etc/sudoers.d/wheel is empty (disaSTIGmedium truncates it with echo -n)."""
    assert (
        file.get_size(SUDOERS_WHEEL) == 0
    ), f"stigcompliance: {SUDOERS_WHEEL} is not empty (size={file.get_size(SUDOERS_WHEEL)})"
