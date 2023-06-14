from helper.utils import read_test_config
import string
import re

def capabilities(client, testconfig, non_chroot):
    """ Test if only the defined capabilities are set"""
    (exit_code, output, error) = client.execute_command(
        "sudo -u root find /boot /etc /usr /var -type f -exec /usr/sbin/getcap {} \\;", quiet=True)
    assert exit_code == 0, f"no {error=} expected"

    # get capabilities.list config from enabled features
    features = testconfig["features"]
    capabilities = read_test_config(features, "capabilities")
    # and remove duplicates
    capabilities = list(set(capabilities))

    cap_found = []
    cap_notfound = []
    for line in output.splitlines():
        line.strip(string.whitespace)
        for cap in capabilities:
            match = re.fullmatch(cap, line)
            if match:
                break
        if match:
            cap_found.append(line)
        else:
            cap_notfound.append(line)

    assert len(cap_found) == len(capabilities), ("Found capabilities " +
        "do not match expected capabilities. Found: " +
        f"{', '.join(cap_found)} Expected: {', '.join(capabilities)}")

    assert len(cap_notfound) == 0, ("Capabilities " +
        f"{', '.join(cap_notfound)} are not in expected capabilities list")
