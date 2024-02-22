from helper.utils import execute_local_command


def test_proc(client, container, testconfig):
    """ Test for an empty /proc within the given rootfs tarball """
    # Get image path from config for platform
    image_path = testconfig.get("image")
    assert image_path, f"Could not get {image_path}."

    # Execute local command (this does not need to be
    # performed within a platform itself) since "/proc"
    # will never be empty on a running/used system.
    cmd = f"tar tf {image_path}"
    rc, out = execute_local_command(cmd)

    # Only proceed if local command was sucessfull
    assert rc == 0, f"Could not unpack {image_path}."

    # Validate for captures of any lines starting with "proc/"
    matches = []
    for line in out.split('\n'):
        if line.startswith("proc/"):
            matches.append(line)

    # Only "/proc/" as an empty directory should be found
    assert len(matches) == 1, f"/proc is not empty. Found: {matches}"
