from helper.utils import read_test_config


def capabilities(client, testconfig, non_chroot):
    """Test if only the defined capabilities are set"""
    (exit_code, output, error) = client.execute_command(
        "sudo -u root find /boot /etc /usr /var -type f -exec /usr/sbin/getcap {} \\;",
        quiet=True,
    )
    assert exit_code == 0, f"no {error=} expected"

    # get capabilities.list config from enabled features
    features = testconfig["features"]
    deduplicated_capabilities = set(read_test_config(features, "capabilities"))

    cap_found = []
    cap_notfound = []

    for line in output.split():
        if line in deduplicated_capabilities:
            cap_found.append(line)
        else:
            cap_notfound.append(line)

    assert len(cap_found) == len(deduplicated_capabilities), (
        "Found capabilities "
        + "do not match expected capabilities. Found: "
        + f"{', '.join(cap_found)} Expected: {', '.join(deduplicated_capabilities)}"
    )

    assert len(cap_notfound) == 0, (
        "Capabilities "
        + f"{', '.join(cap_notfound)} are not in expected capabilities list"
    )
