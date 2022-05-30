import re
import string

from helper import utils

def kernel_config(client, testconfig):
    """Read desired kernel config options from file and compare them against
    the kernel config in /boot"""
    (exit_code, output, error) = client.execute_command(
        "cat /boot/config-*", quiet=True)
    assert exit_code == 0, f"no {error=} expected"

    enabled_features = testconfig["features"]

    expected_config = utils.read_test_config(
        enabled_features, 'kernel-config', '.txt',
        filter_comments = False)

    config_dict = _to_dict(output)
    expected_config_dict = _to_dict(expected_config)

    not_matching = []
    for key, value in expected_config_dict.items():
        if key in config_dict:
            if (value == "n" or value == "is not set") and \
                (config_dict[key] == "n" or \
                config_dict[key] == "is not set"):
                continue
            if not config_dict[key] == value:
                not_matching.append(key)

    assert len(not_matching) == 0, \
            (f"the following kernel config parameters do not match: " +
            f"{', '.join(not_matching)}")
            

def _to_dict(input):
    """convert input into a dictionary where the first entry of a line is
    used as key, remove everything that is not a CONFIG_ parameter"""
    input_list = []
    if not type(input) == list:
        for line in input.splitlines():
            input_list.append(line)
    else:
        input_list = input
    output = {}
    for entry in input_list:
        if not re.match(r".*CONFIG_", entry):
            continue
        entry = re.sub("^# *", "", entry)
        entry = entry.replace("=", " ")
        entry_as_list = entry.split(" ", 1)
        output.update({entry_as_list[0] : \
            entry_as_list[1].strip(string.whitespace)})
    return output
