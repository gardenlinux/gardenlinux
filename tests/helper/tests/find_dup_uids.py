def find_dup_uids(client, non_local):
    """find duplicated uids"""
    # Call binary on remote and get passwd
    (exit_code, output, error) = client.execute_command(
        "getent passwd", quiet=True)
    assert exit_code == 0, f"no {error=} expected"

    # Validate the output content
    match = {} 
    for line in output.splitlines():
        line = line.split(":")
        uid = line[2]
        user = line[0]
        if not match.get(uid):
            match[uid] = [user]
        else:
            match[uid].append(user)

    # Validate for each UID for multiple users
    for key in match:
        assert len(match[key]) == 1, \
            f"UID {str(key)} is used multiple times in /etc/passwd"