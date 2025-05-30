import hashlib

def ssh_authorized(client, testconfig, provisioner_chroot):
    """Test to that not user has an authorized_keys file and also check
    that the test_authorized_keys file injected for testing wasn't modified"""
    # get passwd
    (exit_code, output, error) = client.execute_command(
        "getent passwd", quiet=True)
    assert exit_code == 0, f"no {error=} expected"

    # check if users with login shell have authorized_keys file
    have_authorized_keys = []
    for line in output.split('\n'):
        if line != '' and not ("/bin/false" in line or 
                            "nologin" in line or "/bin/sync" in line):
            line = line.split(":")
            home_dir = line[5]
            user = line[0]
            if _has_authorized_keys(client, home_dir):
                have_authorized_keys.append(user)

    assert len(have_authorized_keys) == 0, (f"following users have " +
                f"authorized_keys defined {' '.join(have_authorized_keys)}")

    # check that the injected authorized_keys file is not modified
    ssh_key_path = testconfig["ssh"]["ssh_key_filepath"]
    with open(f"{ssh_key_path}.pub", "rb") as authorized_keys_file:
        sha256_local = hashlib.sha256(
                        authorized_keys_file.read()).hexdigest()

    (exit_code, output, _) = client.execute_command(
        f"sha256sum $HOME/.ssh/test_authorized_keys", quiet=True)
    assert exit_code == 0, f"no {error=} expected"
    
    assert sha256_local == output.split(' ', 1)[0], ("the authorized_keys " +
                "file injected for testing was modified")


def _has_authorized_keys(client, home_dir):
    files = ["authorized_keys", "authorized_keys2"]
    for file in files:
        (exit_code, _, _) = client.execute_command(
            f"ls {home_dir}/.ssh/{file}", quiet=True)
        if exit_code == 0:
            return True
    return False