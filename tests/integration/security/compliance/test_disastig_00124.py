"""
Ref: SRG-OS-000312-GPOS-00124

Verify the operating system allows operating system admins to change security
attributes on users, the operating system, or the operating system's
components.
"""

import pytest


@pytest.mark.feature("server or disaSTIGmedium")
def test_sudo_installed(file):
    """Verify the sudo binary is installed and executable."""
    assert file.is_executable("/usr/bin/sudo")


@pytest.mark.feature(
    "server and not disaSTIGmedium",
    reason="disaSTIGmedium intentionally empties the wheel file (SRG-OS-000373-GPOS-00156 takes precedence)",
)
def test_sudo_has_wheel_group_enabled(parse_file):
    """Verify sudoers grants the wheel group access."""
    lines = parse_file.lines("/etc/sudoers.d/wheel")
    assert "%wheel" in lines
