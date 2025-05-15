import logging
import time

import pytest
from helper.utils import execute_remote_command

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


@pytest.fixture
def iscsi_device(client):
    logger.info("Starting iSCSI setup test")
    execute_remote_command(
        client, "/usr/sbin/start-stop-daemon --start --exec /usr/sbin/tgtd || /bin/true"
    )

    execute_remote_command(
        client, "dd if=/dev/zero of=/tmp/iscsi_disk.img bs=1 count=0 seek=1G"
    )

    iscsi_config = """<target iqn.2025-04.localhost:storage.disk1>
            backing-store /tmp/iscsi_disk.img
            initiator-address 127.0.0.1
        </target>"""
    execute_remote_command(client, f"sudo mkdir -p /etc/tgt/conf.d")
    execute_remote_command(
        client, f"echo '{iscsi_config}' | sudo tee /etc/tgt/conf.d/iscsi_target.conf"
    )
    execute_remote_command(client, "sudo /usr/sbin/tgt-admin --update ALL")
    execute_remote_command(client, "sudo tgtadm --mode target --op show")
    execute_remote_command(
        client, "sudo iscsiadm -m discovery -t sendtargets -p 127.0.0.1"
    )
    output = execute_remote_command(client, "sudo iscsiadm -m node --login")
    logger.info(f"iscsiadm login: {output}")
    execute_remote_command(client, "sleep 10")

    yield

    execute_remote_command(client, "sudo iscsiadm --mode node --logout")
    execute_remote_command(
        client,
        "/usr/sbin/start-stop-daemon --stop --quiet --oknodo --exec /usr/sbin/tgtd",
    )
    execute_remote_command(client, f"sudo rm -rf /etc/tgt/conf.d")


def test_iscsi_setup(client, non_provisioner_chroot, iscsi_device):
    output_before = execute_remote_command(client, "ls -la /dev/disk/by-path/")
    logger.info(f"Block devices before rescan: {output_before}")
    assert "iscsi-iqn" not in output_before, "Unexpected iscsi-iqn before rescan"

    session_id = execute_remote_command(
        client, "sudo iscsiadm -m session | awk '{print $2}'"
    )
    session_id = session_id.strip("[]")
    assert session_id, "Failed to get session ID"

    output = execute_remote_command(
        client, f"sudo iscsiadm -m session -r {session_id} --rescan"
    )
    logger.info(f"Rescan output: {output}")
    time.sleep(1)
    output_after = execute_remote_command(client, "ls -la /dev/disk/by-path/")
    logger.info(f"Block devices after rescan: {output_after}")
    assert "iscsi-iqn" in output_after, "Expected iscsi-iqn after rescan"
