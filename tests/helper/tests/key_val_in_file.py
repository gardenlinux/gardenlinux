import re


def key_val_in_file(client, fname, args, invert=False, ignore_missing=False):
    """ Performing unit test to find key/val in files """
    content = _get_content_remote_file(client, fname)

    if not content:
        assert not content and ignore_missing, f"Content or file not found: {fname}."
    else:
        key_values = _get_key_values_from_content(content, args)
        content_keys = set(key_values.keys())
        arg_keys = set(args.keys())

        if not invert:
            assert content_keys == arg_keys, f"Could not find {args} in {fname}."
        else:
            assert len(content_keys) == 0, f"Found {args} in {fname}."


def _get_content_remote_file(client, fname):
    """ Get the content of a remote file by the given file name """
    cmd = f"cat {fname}"
    (exit_code, output, error) = client.execute_command(
        cmd, quiet=True)
    if not "No such file or directory" in error:
        return output


def _get_key_values_from_content(content, args):
    result = dict()
    content_lines = content.split('\n')
    for line in content_lines:
        line_key = re.sub(r'(\w*).*', '\\1', line)

        if line_key in args.keys() and args[line_key] in line:
            result[line_key] = args[line_key]
    return result
