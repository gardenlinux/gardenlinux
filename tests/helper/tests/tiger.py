import os
from helper import utils

def tiger(client, testconfig):
    """Run tiger to test for system security vulnerabilities"""
    utils.AptUpdate(client)
    (exit_code, output, error) = client.execute_command(
        "apt-get install -y --no-install-recommends tiger",
        quiet=True)
    assert exit_code == 0, f"no {error=} expected"

    enabled_features = testconfig["features"]

    # merge tiger config files for enabled features
    with open("/tmp/tigerrc", "w") as merged_config:
        for feature in enabled_features:
            path = (f"/gardenlinux/features/{feature}" +
                    "/test/tiger.d/tigerrc")
            if os.path.isfile(path):
                with open(path) as feature_config:
                    merged_config.write(feature_config.read())

    # upload tiger config file
    client.remote_path = "/tmp"
    client.bulk_upload(["/tmp/tigerrc"])

    # unmount directories that make the tiger checks fail
    (exit_code, output, error) = client.execute_command(
        "unshare --mount --propagation unchanged bash -c 'umount " +
        "-l /sys /dev /proc && tiger -c /tmp/tigerrc -q'", quiet=True)
    assert exit_code == 0, f"no {error=} expected"

    (exit_code, output, error) = client.execute_command(
        "grep -hw FAIL /var/log/tiger/security.report.*", quiet=True)
    assert output == '', f"tiger detected the following errors: {output}"