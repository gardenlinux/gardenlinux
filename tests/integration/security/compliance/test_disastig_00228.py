import glob

"""
Ref: SRG-OS-000480-GPOS-00228

Verify the operating system defines default permissions for all authenticated
users in such a way that the user can only read and modify their own files.
"""


def test_umask_is_restrictive_enough(parse_file):
    config = parse_file.parse("/etc/login.defs", format="spacedelim")
    assert config["UMASK"] == "027"


def test_skeleton_files_are_not_world_writable(file):
    assert file.has_permissions("/etc/skel", "755")
    for f in glob.glob("/etc/skel/.*"):
        assert file.has_permissions(
            f, "640"
        ), f"File permissions for {f} should not allow write access for 'others', current mode is {file.get_mode(f)}"
