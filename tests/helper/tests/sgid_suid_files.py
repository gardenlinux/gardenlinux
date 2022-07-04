def sgid_suid_files(client, id_type, whitelist_files):
    """ Performing unit test for feature: Fedramp """
    if id_type == 'sgid':
        remote_files = _get_remote_files(client, "-2000")
        _val_whitelist_files(remote_files, whitelist_files)
    if id_type == 'suid':
        remote_files = _get_remote_files(client, "-4000")
        _val_whitelist_files(remote_files, whitelist_files)


def _get_remote_files(client, perm):
    """ Get remote files of given attribute """
    files = []
    cmd_find = f"find / -type f -perm {perm} -exec "
    cmd_stat = "stat -c '%n,%U,%G' {} \\; 2> /dev/null"
    cmd = cmd_find + cmd_stat
    (exit_code, output, error) = client.execute_command(
        cmd, quiet=True)

    for line in output.split('\n'):
        if line != '':
            files.append(line)
    return files


def _val_whitelist_files(remote_files, whitelist_files):
    """ Validates that remotly found files are in whitelist """
    found_files = []
    for file in remote_files:
        if file not in whitelist_files:
            found_files.append(file)
    assert not found_files, f"{found_files}"
