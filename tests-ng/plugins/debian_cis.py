import yaml


def DebianCIS(client, args):
    """Performing unit test for feature: CIS"""

    # Defining vars from PyTest parametrize
    git_debian_cis =  args["git_debian_cis"]
    git_debian_cis_branch = args["git_debian_cis_branch"]
    config_src = args["config_src"]
    config_dst = args["config_dst"]
    script_src = args["script_src"]
    script_dst = args["script_dst"]

    # /tmp has 'noexec' flag; therefore we need to
    # call each script with bash.
    cmd_debian_cis = "for i in `ls /tmp/debian-cis/bin/hardening/*.sh`; do /bin/bash $i; done"

    # Fetch DebianCIS GIT repository from upstream
    (exit_code, output, error) = client.execute_command(
        f"cd /tmp/ && git clone -b {git_debian_cis_branch} {git_debian_cis}")
    assert exit_code == 0, f"no {error=} expected"

    # Copy Debian CIS config files
    client.remote_path = f"{config_dst}"
    client.bulk_upload([config_src])

    # Copy Debian CIS check_scripts
    client.remote_path = f"{script_dst}"
    client.bulk_upload([script_src])

    # Write DebianCIS config
    (exit_code, output, error) = client.execute_command(
        "echo CIS_ROOT_DIR='/tmp/debian-cis' > /etc/default/cis-hardening")
    assert exit_code == 0, f"no {error=} expected"

    # Execute all test scripts
    (exit_code, output, error) = client.execute_command(f"{cmd_debian_cis}")

    # Validate that no test script failed
    assert not "Check Failed" in output, ("CIS Test failed")
