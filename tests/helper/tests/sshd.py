import re

def sshd(client, expected):
    """Tests if a sshd option is set to an expected value. The expected
    option value pair is a tuple, the sshd_config is conterted into a list 
    of tuples"""

    (exit_code, output, error) = client.execute_command("sshd -T",
                                                        quiet=True)
    assert exit_code == 0, f"no {error=} expected"

    sshd_config = _create_list_of_tuples(output)

    expected = (expected[0].lower(), _normalize_value(expected[1]))

    assert expected in sshd_config, f"{expected} not found in sshd_config"


def _create_list_of_tuples(input):
    """Takes a multiline string and returns a list containing every line 
    as a tuple. The 1st value of the tuple is the ssh option, the 2nd is
    value"""
    out = []
    for line in input.splitlines():
        l = line.split(' ', 1)
        out.append((l[0], _normalize_value(l[1])))
    return out

def _normalize_value(string):
    """Convert a given string.
    All elements will be converted to lower case and the string will be
    returned as a set. If the element contains a comma separated string,
    it will be split into a list first."""
    normalized = string.lower().split(" ")
    if len(normalized) == 1 and re.match(r".*,.*",normalized[0]):
        value_as_set = set(normalized[0].split(','))
    else:
        value_as_set = set(normalized)
    return value_as_set