from helper.utils import read_test_config
import string

def capabilities(client, testconfig):
    """ Test if only the defined capabilities are set"""
    (exit_code, output, error) = client.execute_command(
        "find /boot /etc /usr /var -type f -exec getcap {} \\;", quiet=True)
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
        if line not in capabilities:
            cap_notfound.append(line)
        if line in capabilities:
            cap_found.append(line)

    assert len(cap_found) == len(capabilities), ("Found capabilities " +
        "do not match expected capabilities. Found: " +
        f"{', '.join(cap_found)} Expected: {', '.join(capabilities)}")

    assert len(cap_notfound) == 0, ("Capabilities " +
        f"{', '.join(cap_notfound)} are not in expected capabilities list")
