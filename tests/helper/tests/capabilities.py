from helper.utils import read_test_config


def capabilities(client, testconfig):
    """Test if only the defined capabilities are set"""
    (exit_code, output, error) = client.execute_command(
        "sudo -u root find /boot /etc /usr /var -type f -exec /usr/sbin/getcap {} \\;",
        quiet=True,
    )
    assert exit_code == 0, f"no {error=} expected"

    # get capabilities.list config from enabled features
    features = testconfig["features"]
    depublicated_capabilities = set(read_test_config(features, "capabilities"))

    cap_found = []
    cap_notfound = []

    for line in output.splitlines():
        line = line.strip()
        if line in depublicated_capabilities:
            cap_found.append(line)
        cap_notfound.append(line)

    assert len(cap_found) == len(depublicated_capabilities), (
        "Found capabilities "
        + "do not match expected capabilities. Found: "
        + f"{', '.join(cap_found)} Expected: {', '.join(depublicated_capabilities)}"
    )

    assert len(cap_notfound) == 0, (
        "Capabilities "
        + f"{', '.join(cap_notfound)} are not in expected capabilities list"
    )
