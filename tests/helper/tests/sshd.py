def sshd(client, expected):
    """Tests if a sshd option is set to an expected value. The expected
    option value string and the sshd_config are conterted into lists of 
    tuples"""

    (exit_code, output, error) = client.execute_command("sudo -u root /usr/sbin/sshd -T",
                                                        quiet=True)
    assert exit_code == 0, f"no {error=} expected"

    sshd_config = _create_list_of_tuples(output)

    def check_option(option, config):
        if isinstance(option, list):
            return any(_normalize_line(opt.lower()) in config for opt in option)
        else:
            return _normalize_line(option.lower()) in config

    assert check_option(expected, sshd_config), f"{expected} not found in sshd_config"


def _create_list_of_tuples(input):
    """Takes a multiline string and returns a list containing every line 
    as a tuple. The 1st value of the tuple is the ssh option, the 2nd is
    value"""
    out = []
    for line in input.lower().splitlines():
        out.append(_normalize_line(line))
    return out

def _normalize_line(line):
    l = line.split(' ', 1)
    option = l[0]
    value = l[1]
    normalized_value = _normalize_value(value)
    return (option, normalized_value)

def _normalize_value(string):
    """Convert a given string.
    The string will be returned as a set. If the element contains a comma
    separated string, it will be split into a list first."""
    normalized = string.split(" ")
    if len(normalized) == 1 and "," in normalized[0]:
        value_as_set = set(normalized[0].split(','))
    else:
        value_as_set = set(normalized)
    return value_as_set
