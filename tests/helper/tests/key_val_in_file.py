def key_val_in_file(client, fname, dict):
    """ Performing unit test to find key/val in files """
    content = _get_content_remote_file(client, fname)
    _get_key_val_from_content(content, dict, fname)


def _get_content_remote_file(client, fname):
    """ Get the content of a remote file by the given file name """
    cmd = f"cat {fname}"
    (exit_code, output, error) = client.execute_command(
        cmd, quiet=True)
    if not "No such file or directory" in error:
        return output


def _get_key_val_from_content(content, dict, fname):
    """ Validates if key/val are present in content """
    for k in dict:
        for line in content.split('\n'):
            if line.startswith(k):
                assert dict[k] in line, f"Could not find {dict} in {fname}."
