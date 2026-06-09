import glob

import pytest

"""
Ref: SRG-OS-000480-GPOS-00228

Verify the operating system defines default permissions for all authenticated
users in such a way that the user can only read and modify their own files.
"""


def test_umask_is_restrictive_enough(parse_file):
    config = parse_file.parse("/etc/login.defs", format="spacedelim")
    assert config["UMASK"] in ("027", "077")


def test_skeleton_directory_is_not_world_writable(file):
    assert file.has_permissions("/etc/skel", "755")


def test_skeleton_files_are_not_world_writable(file):
    for f in glob.glob("/etc/skel/.*"):
        assert file.has_permissions(f, "640") or file.has_permissions(
            f, "644"
        ), f"Wrong file permissions for {f}: {file.get_mode(f)}"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-login-defs-umask"])
@pytest.mark.feature("disaSTIGmedium", reason="077 umask is enforced by disaSTIGmedium")
def test_login_defs_umask_is_077(parse_file) -> None:
    """Verify UMASK in /etc/login.defs is set to 077 (SRG-OS-000480-GPOS-00228)."""
    config = parse_file.parse("/etc/login.defs", format="spacedelim")
    assert (
        config["UMASK"] == "077"
    ), f"stigcompliance: UMASK in /etc/login.defs is {config['UMASK']!r}, expected '077'"
