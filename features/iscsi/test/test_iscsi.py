import pytest
from helper.utils import execute_remote_command
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


@pytest.fixture
def iscsi_device(client):
    logger.info("Starting iSCSI setup test")
    execute_remote_command(
        client, "start-stop-daemon --start --exec /usr/sbin/tgtd || /bin/true"
    )

    execute_remote_command(
        client, "dd if=/dev/zero of=/tmp/iscsi_disk.img bs=1 count=0 seek=1G"
    )

    iscsi_config = """<target iqn.2025-04.localhost:storage.disk1>
            backing-store /tmp/iscsi_disk.img
            initiator-address 127.0.0.1
        </target>"""
    execute_remote_command(
        client, f"sudo bash -c \"echo '{iscsi_config}' > /etc/tgt/conf.d/iscsi_target.conf\""
    )
    execute_remote_command(client, "sudo /usr/sbin/tgt-admin --update ALL")
    execute_remote_command(client, "sudo tgtadm --mode target --op show")
    execute_remote_command(client, "sudo iscsiadm -m discovery -t sendtargets -p 127.0.0.1")
    output = execute_remote_command(client, "sudo iscsiadm -m node --login || /bin/true")

    yield

    execute_remote_command(client, "sudo iscsiadm --mode node --logout")
    execute_remote_command(
        client, "start-stop-daemon --stop --quiet --exec /usr/sbin/tgtd"
    )


def test_iscsi_setup(client, non_provisioner_chroot, iscsi_device):
    output = execute_remote_command(client, "lsblk")
    logger.info(f"Block devices before rescan: {output}")
    assert "sdb" not in output, "Unexpected /dev/sdb before rescan"

    session_id = execute_remote_command(
        client, "sudo iscsiadm -m session | awk '{print $2}'"
    )
    session_id = session_id.strip("[]")
    assert session_id, "Failed to get session ID"

    output = execute_remote_command(
        client, f"sudo iscsiadm -m session -r {session_id} --rescan"
    )
    logger.info(f"Rescan output: {output}")

    output = execute_remote_command(client, "lsblk")
    logger.info(f"Block devices after rescan: {output}")
    assert "sdb" in output, "Expected /dev/sdb after rescan"
