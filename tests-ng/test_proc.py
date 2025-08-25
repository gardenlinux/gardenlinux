import pytest

from plugins.shell import ShellRunner

@pytest.mark.feature("not booted")
def test_proc(shell: ShellRunner):
    """ Test for an empty /proc within the given rootfs tarball """    

    # Execute local command (this does not need to be
    # performed within a platform itself) since "/proc"
    # will never be empty on a running/used system.
    cmd = "ls -1 /proc"
    result = shell(cmd=cmd, shell=False, capture_output=True, ignore_exit_code=True)

    # Within "/proc/" no files or directories should be found. One linefeed is always produced.
    matches = result.stdout.split("\n")
    assert len(matches) == 1, f"/proc is not empty. Found: {len(matches)}"
