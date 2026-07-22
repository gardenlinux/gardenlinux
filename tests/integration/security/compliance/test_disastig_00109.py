"""
Ref: SRG-OS-000279-GPOS-00109

Verify the operating system initiates a session lock after a period of
inactivity. Setting TMOUT=900 in a profile.d script ensures interactive
shell sessions time out after 15 minutes of inactivity.
"""

import pytest


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-profile-terminal-tmout"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="terminal timeout is configured by disaSTIGmedium"
)
@pytest.mark.security_id(203683)
def test_terminal_tmout_profile_sets_tmout_900(parse_file) -> None:
    """Verify the profile.d snippet sets TMOUT=900 (15 min)."""
    assert "TMOUT=900" in parse_file.lines("/etc/profile.d/99-terminal_tmout.sh")
