import pytest
import os

from plugins.booted import is_system_booted

@pytest.mark.root
def test_image_proc_is_empty(remounted_root):
    """
    Test for an empty /proc within the given rootfs tarball. Since /proc is mounted 
    we remount / temporarily. This allows to check if the image comes with an empty 
    proc directory.
    """
    temp_proc = os.path.join(remounted_root, "proc")

    # We need the clean /proc directory in the chroot
    assert os.path.ismount(temp_proc) == False, f"{temp_proc} must not be mounted"

    # Execute local file listing (this does not need to be
    # performed within a platform itself) since "/proc"
    # will never be empty on a running/used system.
    proc_files: list[str] = os.listdir(temp_proc)

    # Within temporary "/proc" no files or directories should be found.
    assert len(proc_files) == 0, f"{temp_proc} is not empty."

@pytest.mark.root
@pytest.mark.booted
def test_running_proc_is_not_empty():
    """
    negative test as mounted proc should contain expected files
    """
    root_proc = "/proc"
    root_proc_files: list[str] = os.listdir(root_proc)
    assert len(root_proc_files) >= 0, f"{root_proc} should contain files."
    assert all(expected_procfile in root_proc_files for expected_procfile in ["version", "uptime"]), f"{root_proc} does not contain the usual files."