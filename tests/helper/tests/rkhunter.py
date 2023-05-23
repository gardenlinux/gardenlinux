import os
from helper import utils
import logging

logger = logging.getLogger(__name__)

# Execute the rkhunter test only on chroot
# since it must install some packages that
# may not be possible on running machines.
def rkhunter(client, testconfig, chroot, non_container, non_chroot):
    """Run rkhunter to test for rootkits"""
    utils.AptUpdate(client)
    utils.install_package_deb(client, "rkhunter")

    enabled_features = testconfig["features"]

    # merge rkhunter config files for enabled features
    with open("/tmp/rkhunter.conf", "w") as merged_config:
        for feature in enabled_features:
            path = (f"/gardenlinux/features/{feature}" +
                    "/test/rkhunter.d/rkhunter.conf")
            if os.path.isfile(path):
                with open(path) as feature_config:
                    merged_config.write(feature_config.read())

    # upload rkhunter config file
    client.remote_path = "/tmp"
    client.bulk_upload(["/tmp/rkhunter.conf"])

    # causes rkhunter to update its data file of stored values with the
    # current values
    utils.execute_remote_command(client, "rkhunter --configfile " +
                    "/tmp/rkhunter.conf --propupd -q")

    # run the actual rkhunter tests
    (_, _, _) = client.execute_command(
        "rkhunter --configfile /tmp/rkhunter.conf --enable " +
        "system_configs_ssh,group_accounts,filesystem,group_changes," +
        "passwd_changes,startup_malware,system_configs_ssh,properties -q " +
        "--rwo --noappend-log 2>/dev/null", quiet=True)

    # check the rkhunter log file for any warnings
    (_, output, _) = client.execute_command(
        "grep -w Warning: /var/log/rkhunter.log", quiet=True)

    # print the rkhunter warnings before failing the test
    if output != '':
        for line in output.splitlines():
            logger.error(line.split(' ', 1)[1])

    assert output == '', f"rkhunter has warnings"
