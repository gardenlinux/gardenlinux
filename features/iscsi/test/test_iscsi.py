import pytest
from helper.utils import execute_remote_command
from helper.dependencies import (
    install_test_dependencies,
    uninstall_test_dependencies,
    create_overlay_fs,
    cleanup_overlay_fs,
)
from helper.utils import validate_systemd_unit
import logging
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


@pytest.fixture(scope="function")
def cleanup_iscsi(client):
    yield
    logger.info("Cleaning up potential leftover iSCSI state after test...")

    logout_output = execute_remote_command(client, "iscsiadm -m session")
    if logout_output:
        logger.info("Logging out of existing iSCSI sessions...")
        execute_remote_command(client, "iscsiadm -m node --logoutall=all")
        time.sleep(1)

    _, mount_output = execute_remote_command(
        client, "mount | grep 'on /mnt '", skip_error=True
    )
    if mount_output:
        logger.info("Unmounting /mnt...")
        execute_remote_command(client, "umount /mnt")

    logger.info("Removing test artifacts...")
    execute_remote_command(client, "rm -f /mnt/yayitworks /srv/iscsi_disk.img")

    execute_remote_command(client, "rm -f /etc/tgt/conf.d/iscsi_target.conf")

    logger.info("Deleting iSCSI node to clean persistent state...")
    execute_remote_command(
        client,
        "iscsiadm -m node -o delete --targetname iqn.2025-04.localhost:storage.disk1 --portal 127.0.0.1:3260",
    )

    logger.info("Restarting tgt service...")
    execute_remote_command(client, "systemctl restart tgt")
    time.sleep(1)

    logger.info("iSCSI cleanup completed.")
    uninstall_test_dependencies(client, ["tgt"])
    # cleanup_overlay_fs(client)


def test_iscsi_setup(client, cleanup_iscsi, non_provisioner_chroot):
    create_overlay_fs(client)
    install_test_dependencies(client, ["tgt"])
    execute_remote_command(client, "systemctl start tgt")
    validate_systemd_unit(client, "tgt", "running")

    output = execute_remote_command(
        client, "dd if=/dev/zero of=/srv/iscsi_disk.img bs=1 count=0 seek=1G"
    )
    logger.info(f"Disk image creation output: {output}")

    iscsi_config = """<target iqn.2025-04.localhost:storage.disk1>
        backing-store /srv/iscsi_disk.img
        initiator-address 127.0.0.1
    </target>"""
    output = execute_remote_command(
        client, f"echo '{iscsi_config}' > /etc/tgt/conf.d/iscsi_target.conf"
    )
    logger.info(f"iSCSI target configuration output: {output}")

    output = execute_remote_command(client, "/usr/sbin/tgt-admin --update ALL")
    logger.info(f"tgt-admin update output: {output}")

    output = execute_remote_command(client, "tgtadm --mode target --op show")
    logger.info(f"tgtadm verification output: {output}")

    output = execute_remote_command(
        client, "iscsiadm -m discovery -t sendtargets -p 127.0.0.1"
    )
    logger.info(f"iSCSI discovery output: {output}")

    output = execute_remote_command(client, "iscsiadm -m node --login")
    logger.info(f"iSCSI login output: {output}")

    output = execute_remote_command(client, "lsblk")
    logger.info(f"Block devices before rescan: {output}")
    assert "sdb" not in output, "Unexpected /dev/sdb before rescan"

    session_id = execute_remote_command(
        client, "iscsiadm -m session | awk '{print $2}'"
    ).strip("[]")

    output = execute_remote_command(
        client, f"iscsiadm -m session -r {session_id} --rescan"
    )
    logger.info(f"Rescan output: {output}")

    output = execute_remote_command(client, "lsblk")
    logger.info(f"Block devices after rescan: {output}")
    assert "sdb" in output, "Expected /dev/sdb after rescan"
