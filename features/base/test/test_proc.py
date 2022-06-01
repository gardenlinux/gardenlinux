from helper.utils import get_artifact_name
from helper.utils import get_local_command_output


def test_proc(client):
    """ Test for an empty /proc within the given rootfs tarball """
    artifact_name = get_artifact_name(client)
    artifact_path = f"/gardenlinux/.build/{artifact_name}.tar.xz"

    # Execute local command (this does not need to be
    # performed within a platform itself) since "/proc"
    # will never be empty on a running/used system.
    cmd = f"tar tf {artifact_path}"
    rc, out = get_local_command_output(cmd)

    # Only proceed if local command was sucessfull
    assert rc == 0, f"Could not unpack {artifact_path}."

    # Validate for captures of any "proc/" content
    matches = []
    for line in out.split('\n'):
        if "proc/" in line:
            matches.append(line)

    # Only "/proc/" as an empty directory should be found
    assert len(matches) == 1, f"/proc is not empty. Found: {matches}"
