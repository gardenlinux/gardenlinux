import re


def file_content(client, fname, args, invert=False, ignore_missing=False, only_line_match=False, ignore_comments=False):
    """ Performing unit test to find key/val in files """
    content = _get_content_remote_file(client, fname)

    if not content:
        assert not content and ignore_missing, f"Content or file not found: {fname}."
    else:
        if only_line_match:
            line_match = _get_line_match(content, args)
            if not invert:
                assert line_match, f"Could not find line {args} in {fname}."
            else:
                assert not line_match, f"Found line {args} in {fname}, but should not be present."
        else:
            key_values = _get_key_values_from_content(content, args, ignore_comments)
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


def _get_key_values_from_content(content, args, ignore_comments):
    """ Get key/val from content and validate matches by args """
    result = dict()
    content_lines = content.split('\n')
    for line in content_lines:
        if ignore_comments:
            line_key = re.sub(r'#? *(\w*).*', '\\1', line)
        else:
            line_key = re.sub(r'(\w*\.?\w*).*', '\\1', line)

        if line_key in args.keys() and args[line_key] in line:
            result[line_key] = args[line_key]
    return result


def _get_line_match(content, compare_line):
    """ Normalize line and compare for matches in line """
    content_lines = content.split('\n')
    for line in content_lines:
        # Remove tabs and newlines from line to compare
        line = re.sub("\s+"," ", line)
        if compare_line in line:
            return True
    return False
