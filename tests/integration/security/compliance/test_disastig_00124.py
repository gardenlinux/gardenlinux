"""
Ref: SRG-OS-000312-GPOS-00124

Verify the operating system allows operating system admins to change security
attributes on users, the operating system, or the operating system's
components.
"""


def test_sudo_installed(dpkg):
    assert dpkg.package_is_installed("sudo")
