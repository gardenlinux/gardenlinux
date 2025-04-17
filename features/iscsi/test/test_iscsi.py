import pytest
from helper.namespace import NamespaceSession
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


def test_iscsi_setup(client, non_provisioner_chroot):
    with NamespaceSession(client, packages=["tgt"]) as n:
        logger.info("Starting iSCSI setup test")
        n.run("echo yol_runo")
        n.run("echo yolo > /tmp/yolo.txt")
        n.run("ls -l /tmp/yolo.txt")
        n.run("start-stop-daemon --start --quiet --exec /usr/sbin/tgtd")

        n.run("dd if=/dev/zero of=/srv/iscsi_disk.img bs=1 count=0 seek=1G")

        iscsi_config = """<target iqn.2025-04.localhost:storage.disk1>
                backing-store /srv/iscsi_disk.img
                initiator-address 127.0.0.1
            </target>"""
        n.run(f"echo '{iscsi_config}' > /etc/tgt/conf.d/iscsi_target.conf")
        n.run("/usr/sbin/tgt-admin --update ALL")
        n.run("tgtadm --mode target --op show")
        n.run("iscsiadm -m discovery -t sendtargets -p 127.0.0.1")
        n.run("iscsiadm -m node --login")

        output, exit_code = n.run("lsblk")
        # logger.info(f"Block devices before rescan: {output}")
        assert "sdb" not in output, "Unexpected /dev/sdb before rescan"

        session_id, _ = n.run("iscsiadm -m session | awk '{print $2}'")
        session_id = session_id.strip("[]")
        assert session_id, "Failed to get session ID"


#        output = execute_remote_command(
#           client, f"iscsiadm -m session -r {session_id} --rescan"
#       )
#       logger.info(f"Rescan output: {output}")

#       output = execute_remote_command(client, "lsblk")
#       logger.info(f"Block devices after rescan: {output}")
#       assert "sdb" in output, "Expected /dev/sdb after rescan"
