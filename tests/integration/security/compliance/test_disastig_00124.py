import pytest

"""
Ref: SRG-OS-000312-GPOS-00124

Verify the operating system allows operating system admins to change security
attributes on users, the operating system, or the operating system's
components.
"""


@pytest.mark.feature("server or disaSTIGmedium")
def test_sudo_installed(file):
    assert file.is_executable("/usr/bin/sudo")


@pytest.mark.feature(
    "server and not disaSTIGmedium",
    reason="disaSTIGmedium intentionally empties sudoers.d/wheel to require re-authentication",
)
def test_sudo_has_wheel_group_enabled(parse_file):
    lines = parse_file.lines("/etc/sudoers.d/wheel")
    assert "%wheel" in lines
