import pytest
from plugins.file import File
from plugins.find import Find
from plugins.parse_file import ParseFile


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.root(reason="requires access to /etc/login.defs")
def test_umask_is_restrictive_enough(parse_file: ParseFile):
    """
    As per DISA STIG compliance requirements, the operating system must define default
    permissions for all authenticated users in such a way that the user can only read
    and modify their own files.
    This test verifies that UMASK in /etc/login.defs is set to 027.
    Ref: SRG-OS-000480-GPOS-00228
    """
    config = parse_file.parse("/etc/login.defs", format="spacedelim")
    assert config["UMASK"] == "027", (
        "stigcompliance: UMASK in /etc/login.defs must be 027"
    )


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.root(reason="requires access to /etc/skel")
def test_skeleton_directory_is_not_world_writable(file: File):
    """
    As per DISA STIG compliance requirements, the operating system must define default
    permissions for all authenticated users in such a way that the user can only read
    and modify their own files.
    This test verifies that the skeleton directory /etc/skel is not world-writable.
    Ref: SRG-OS-000480-GPOS-00228
    """
    assert file.has_permissions("/etc/skel", "755"), (
        f"stigcompliance: /etc/skel must have permissions 755, got {file.get_mode('/etc/skel')}"
    )


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.root(reason="requires access to /etc/skel")
def test_skeleton_files_are_not_world_writable(file: File, find: Find):
    """
    As per DISA STIG compliance requirements, the operating system must define default
    permissions for all authenticated users in such a way that the user can only read
    and modify their own files.
    This test verifies that all dotfiles in /etc/skel have permissions 640 or 644.
    Ref: SRG-OS-000480-GPOS-00228
    """
    find.root_paths = "/etc/skel"
    find.entry_type = "files"
    find.pattern = ".*"

    for f in find:
        assert file.has_permissions(f, "640") or file.has_permissions(f, "644"), (
            f"stigcompliance: wrong file permissions for {f}: {file.get_mode(f)}"
        )
