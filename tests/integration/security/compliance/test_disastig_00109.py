import pytest

"""
Ref: SRG-OS-000279-GPOS-00109

Verify the operating system initiates a session lock after a period of
inactivity. Setting TMOUT=900 in a profile.d script ensures interactive
shell sessions time out after 15 minutes of inactivity.
"""

TMOUT_PROFILE = "/etc/profile.d/99-terminal_tmout.sh"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-profile-terminal-tmout"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="terminal timeout is configured by disaSTIGmedium"
)
def test_terminal_tmout_profile_sets_tmout_900(parse_file) -> None:
    """Verify /etc/profile.d/99-terminal_tmout.sh contains TMOUT=900 (SRG-OS-000279-GPOS-00109)."""
    lines = parse_file.lines(TMOUT_PROFILE)
    assert any(
        "TMOUT=900" in line for line in lines
    ), f"stigcompliance: {TMOUT_PROFILE} does not contain 'TMOUT=900'"
